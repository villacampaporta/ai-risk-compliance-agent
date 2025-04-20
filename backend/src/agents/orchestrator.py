import json
import os
import re
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from src.agents.compliance_agent import compliance_agent
from src.agents.fraud_agent import fraud_agent
from src.agents.formatter_agent import formatter_agent
from src.utils.logger import log_event

# Initialize Vertex AI with your project info
vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "us-con-gcp-sbx-0000478-032025"), location="europe-west4")

# System prompt for the orchestrator agent
ORCHESTRATOR_PROMPT = (
    "You are an intelligent orchestrator for agents in a risk management and compliance platform. "
    "Analyze the provided query and decide whether it should be delegated to 'compliance', 'fraud', "
    "or if none of them can address it. Return a JSON with the field 'agent', e.g., {\"agent\": \"compliance\"}. "
    "If not applicable, respond with {\"agent\": \"none\"}."
)

# Initialize the LLM without passing system_prompt in the constructor.
llm = ChatVertexAI(model_name="gemini-2.5-pro-preview-03-25")

def _extract_json(content: str) -> str:
    """
    Strip markdown fences and grab the first {...} block.
    """
    # 1) Look for a ```json ... ``` block
    m = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if m:
        return m.group(1)
    # 2) Fallback: first {...}
    m = re.search(r"(\{.*?\})", content, re.DOTALL)
    if m:
        return m.group(1)
    raise ValueError("No JSON object found in response")

def _unwrap_result(result):
    """
    Given whatever the agent returns, always produce a JSON-serializable type:
    - If it's an AIMessage, return its content string.
    - If it's a dict or list, return it directly.
    - Otherwise, str() it.
    """
    if isinstance(result, AIMessage):
        return result.content
    if isinstance(result, (dict, list, str, int, float, bool, type(None))):
        return result
    return str(result)

def intelligent_orchestrator(query: str, transaction: dict = None) -> str:
    try:
        messages = [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=f"Query: {query}")
        ]
        raw_response = llm.predict_messages(messages)
        log_event("Orchestrator raw response", {"raw_response": raw_response})

        # Clean & parse JSON
        try:
            #json_str = _extract_json(raw_response)
            content = getattr(raw_response, "content", str(raw_response))
            json_str = _extract_json(content)
            log_event("The AI message content is as such:", {"json_str": json_str})
            decision = json.loads(json_str)
        except Exception as e:
            log_event("Failed to parse orchestrator JSON", {"error": str(e), "raw": raw_response})
            decision = {"agent": "none"}
        
        if decision.get("agent") == "compliance":
            return _unwrap_result(compliance_agent(query))
        elif decision.get("agent") == "fraud":
            # Use provided transaction data if available; otherwise, fallback to a dummy transaction.
            if transaction is None:
                transaction = {
                    "amount": 900,
                    "ip_distance": 120,
                    "device_type_id": 2,
                    "time_of_day": 23,
                    "tx_frequency": 5,
                    "merchant_risk": 0.7,
                    "account_age": 500,
                    "location_deviation": 10
                }
            return formatter_agent(query, fraud_agent(transaction) or {}, fraud_agent(transaction))
        else:
            return "I'm sorry, I cannot resolve that query at this time."
    except Exception as e:
        log_event("Error in orchestrator", {"error": str(e)})
        return "Error processing the query."
