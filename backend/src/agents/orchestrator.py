import json
from langchain.chat_models import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage
from src.agents.compliance_agent import compliance_agent
from src.agents.fraud_agent import fraud_agent
from src.utils.logger import log_event

# System prompt para el agente orquestador
ORCHESTRATOR_PROMPT = (
    "Eres un orquestador inteligente de agentes en una plataforma de gestión de riesgos y cumplimiento. "
    "Analiza la consulta proporcionada y decide si debe delegarse a 'compliance', 'fraud' o si ninguno de ellos "
    "puede resolver la consulta. Devuelve un JSON con el campo 'agent', por ejemplo: {\"agent\": \"compliance\"}. "
    "Si no es aplicable, responde {\"agent\": \"none\"}."
)

# Inicialización del modelo LLM para orquestación
orchestrator_llm = ChatVertexAI(model="chat-bison", system_prompt=ORCHESTRATOR_PROMPT)

def intelligent_orchestrator(query: str) -> str:
    try:
        messages = [
            SystemMessage(content=ORCHESTRATOR_PROMPT),
            HumanMessage(content=f"Consulta: {query}")
        ]
        raw_response = orchestrator_llm.predict_messages(messages)
        log_event("Respuesta orquestador cruda", {"raw_response": raw_response})
        
        try:
            decision = json.loads(raw_response)
        except Exception:
            decision = {"agent": "none"}
        
        if decision.get("agent") == "compliance":
            return compliance_agent(query)
        elif decision.get("agent") == "fraud":
            # En un caso real, se extraerían detalles relevantes de la consulta.
            dummy_transaction = {
                "amount": 900,
                "ip_distance": 120,
                "device_type_id": 2,
                "time_of_day": 23,
                "tx_frequency": 5
            }
            return json.dumps(fraud_agent(dummy_transaction))
        else:
            return "Lo siento, no puedo resolver esa consulta en este momento."
    except Exception as e:
        log_event("Error en el orquestador", {"error": str(e)})
        return "Error al procesar la consulta."
