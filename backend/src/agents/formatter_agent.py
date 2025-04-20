# src/agents/formatter_agent.py
import json
import os
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import SystemMessage, HumanMessage
from src.utils.logger import log_event

# Init Vertex AI (only needs to run once per process)
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "us-con-gcp-sbx-0000478-032025"),
    location="europe-west4"
)

# Formatter LLM
_formatter_llm = ChatVertexAI(model_name="gemini-2.5-pro-preview-03-25")

# System prompt
_FORMATTER_SYSTEM = (
    "You are a seasoned fraud & compliance expert. "
    "A user has asked: {query}\\n"
    "They provided transaction data: {transaction}\\n"
    "The fraud model produced: {prediction}\\n"
    "Draft a clear, professional paragraph that:\n"
    "- Summarizes the risk or recommendation\n"
    "- Explains key factors\n"
    "- Advises next steps"
)

def formatter_agent(query: str, transaction: dict, prediction: dict) -> str:
    """Return a polished answer combining query, transaction, and model output."""
    try:
        # Prepare messages
        human = HumanMessage(content=_FORMATTER_SYSTEM.format(
            query=query,
            transaction=json.dumps(transaction, indent=2),
            prediction=json.dumps(prediction, indent=2)
        ))
        sys    = SystemMessage(content="")  # no extra system needed
        # Call formatter LLM
        ai_msg = _formatter_llm.predict_messages([sys, human])
        log_event("Formatter output", {"response": ai_msg.content})
        return ai_msg.content
    except Exception as e:
        log_event("Formatter error", {"error": str(e)})
        # Fallback to raw prediction
        return json.dumps(prediction)
