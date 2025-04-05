from langchain.chat_models import ChatVertexAI
from src.utils.logger import log_event

# System prompt específico para el agente de cumplimiento
SYSTEM_PROMPT = (
    "Eres un experto en cumplimiento regulatorio. Tu objetivo es analizar consultas relacionadas con "
    "regulaciones financieras y devolver respuestas precisas y contextuales."
)

# Inicialización del modelo LLM para el agente de cumplimiento
llm = ChatVertexAI(model="chat-bison", system_prompt=SYSTEM_PROMPT)

def compliance_agent(query: str) -> str:
    try:
        response = llm.predict(query)
        log_event("Respuesta compliance_agent", {"response": response})
        return response
    except Exception as e:
        log_event("Error en compliance_agent", {"error": str(e)})
        return "Error al analizar la consulta de cumplimiento."
