import os
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage
from src.utils.logger import log_event

from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI with your project info
vertexai.init(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project-id"), location="us-central1")

# System prompt for the compliance agent
SYSTEM_PROMPT = (
    "You are an expert in regulatory compliance. Your goal is to analyze queries related to financial regulations "
    "and provide precise, contextual responses."
)

# Initialize the LLM without the system_prompt parameter
llm = ChatVertexAI(model_name="chat-bison")

def compliance_agent(query: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query)
    ]
    try:
        response = llm.predict_messages(messages)
        log_event("Compliance agent response", {"response": response})
        return response
    except Exception as e:
        log_event("Error in compliance_agent", {"error": str(e)})
        return "Error analyzing the compliance query."
