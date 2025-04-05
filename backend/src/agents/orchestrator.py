import json
import os
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage
from src.agents.compliance_agent import compliance_agent
from src.agents.fraud_agent import fraud_agent
from src.utils.logger import log_event

# Initialize Vertex AI with your project info
vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"), location="us-central1")

# System prompt for the orchestrator agent
ORCHESTRATOR_PROMPT = (
    "You are an intelligent orchestrator for agents in a risk management and compliance platform. "
    "Analyze the provided query and decide whether it should be delegated to 'compliance', 'fraud', "
    "or if none of them can address it. Return a JSON with the field 'agent', e.g., {\"agent\": \"compliance\"}. "
    "If not applicable, respond with {\"agent\": \"none\"}."
)

# Initialize the LLM without passing system_prompt in the constructor.
llm = ChatVertexAI(model_name="chat-bison")

def intelligent_orchestrator(query: str, transaction: dict = None) -> str:
    try:
        messages = [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=f"Query: {query}")
        ]
        raw_response = llm.predict_messages(messages)
        log_event("Orchestrator raw response", {"raw_response": raw_response})
        
        try:
            decision = json.loads(raw_response)
        except Exception:
            decision = {"agent": "none"}
        
        if decision.get("agent") == "compliance":
            return compliance_agent(query)
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
            return json.dumps(fraud_agent(transaction))
        else:
            return "I'm sorry, I cannot resolve that query at this time."
    except Exception as e:
        log_event("Error in orchestrator", {"error": str(e)})
        return "Error processing the query."
