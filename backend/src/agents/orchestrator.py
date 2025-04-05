import json
from langchain.chat_models import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage
from src.agents.compliance_agent import compliance_agent
from src.agents.fraud_agent import fraud_agent
from src.utils.logger import log_event

# System prompt for the orchestrator agent
ORCHESTRATOR_PROMPT = (
    "You are an intelligent orchestrator for agents in a risk management and compliance platform. "
    "Analyze the provided query and decide whether it should be delegated to 'compliance', 'fraud', "
    "or if none of them can address it. Return a JSON with the field 'agent', e.g., {\"agent\": \"compliance\"}. "
    "If not applicable, respond with {\"agent\": \"none\"}."
)

# Initialize the LLM for orchestration
orchestrator_llm = ChatVertexAI(model="chat-bison", system_prompt=ORCHESTRATOR_PROMPT)

def intelligent_orchestrator(query: str) -> str:
    try:
        messages = [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=f"Query: {query}")
        ]
        raw_response = orchestrator_llm.predict_messages(messages)
        log_event("Orchestrator raw response", {"raw_response": raw_response})
        
        try:
            decision = json.loads(raw_response)
        except Exception:
            decision = {"agent": "none"}
        
        if decision.get("agent") == "compliance":
            return compliance_agent(query)
        elif decision.get("agent") == "fraud":
            # For demonstration, using a dummy transaction; in production, extract details from the query.
            dummy_transaction = {
                "amount": 900,
                "ip_distance": 120,
                "device_type_id": 2,
                "time_of_day": 23,
                "tx_frequency": 5,
                "merchant_risk": 0.7,
                "account_age": 500,
                "location_deviation": 10
            }
            return json.dumps(fraud_agent(dummy_transaction))
        else:
            return "I'm sorry, I cannot resolve that query at this time."
    except Exception as e:
        log_event("Error in orchestrator", {"error": str(e)})
        return "Error processing the query."
