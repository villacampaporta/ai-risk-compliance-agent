from langchain.chat_models import ChatVertexAI
from src.utils.logger import log_event

# System prompt for the compliance agent
SYSTEM_PROMPT = (
    "You are an expert in regulatory compliance. Your goal is to analyze queries related to financial regulations and provide precise, contextual responses."
)

# Initialize the LLM for compliance queries
llm = ChatVertexAI(model="chat-bison", system_prompt=SYSTEM_PROMPT)

def compliance_agent(query: str) -> str:
    try:
        response = llm.predict(query)
        log_event("Compliance agent response", {"response": response})
        return response
    except Exception as e:
        log_event("Error in compliance_agent", {"error": str(e)})
        return "Error analyzing the compliance query."
