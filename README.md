# 🛡️ Risk & Compliance Agent

A modular, AI-powered agent system designed to streamline risk management and regulatory compliance for financial institutions. The solution integrates machine learning for real-time fraud detection with natural language processing (NLP) for compliance analysis. It is built using Flask, Python, and Google Cloud Platform (GCP) services.

---

## 📌 Overview

The **Risk & Compliance Agent** is a multi-agent system that:

- ✅ **Monitors transactions in real time** to detect anomalies and potential fraud.
- ⚖️ **Interprets regulatory updates** and provides compliance recommendations using LLMs (LangChain + Vertex AI).
- 🧠 **Routes queries intelligently** using a custom orchestrator that delegates requests based on intent.
- 🔍 **Integrates with BigQuery** to analyze large-scale financial datasets.
- ☁️ **Deploys on GCP** using App Engine or Cloud Run for scalability and resilience.

---

## ✨ Features

- **Modular Architecture** — Clean separation of agents (fraud, compliance, orchestrator).
- **LLM-Based Orchestration** — Uses Gemini 2.5 with system prompts to classify and dispatch queries.
- **Real-Time Scoring** — ML fraud detection with low latency scoring.
- **Streamlit Dashboard** — Rich interactive frontend for non-technical users.
- **GCP-Native Deployment** — Integrates with GCP logging, networking, and autoscaling.

---

## 🗂 Project Structure

```plaintext
backend/
├── app.yaml                  # App Engine configuration
├── Dockerfile                # Container setup
├── requirements.txt          # Python dependencies
├── app.py                    # Flask application factory
└── src/
    ├── config.py             # Runtime configuration
    ├── data/
    │   ├── generate_transactions.py
    │   └── transactions_sample.csv
    ├── model/
    │   ├── model_trainer.py
    │   └── fraud_model.pkl
    ├── agents/
    │   ├── compliance_agent.py
    │   ├── fraud_agent.py
    │   ├── formatter_agent.py
    │   └── orchestrator.py
    ├── endpoints/
    │   ├── transaction_endpoint.py
    │   └── query_endpoint.py
    └── utils/
        ├── logger.py
        ├── security.py
        └── constant.py
frontend/
├── main.py                   # Streamlit UI
├── app.yaml                  # Frontend deployment config
├── requirements.txt
└── .streamlit/secrets.toml
```

---

## ✅ Prerequisites

- Python 3.10+
- [Docker](https://www.docker.com/)
- [Google Cloud SDK](https://cloud.google.com/sdk)
- GCP project with App Engine and billing enabled

---

## 🛠 Installation

```bash
git clone https://github.com/your-username/risk-compliance-agent.git
cd risk-compliance-agent/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🧪 Local Development

### Backend (Flask API)

```bash
python app.py
```

### Endpoints

- Health Check: [http://localhost:8080/health](http://localhost:8080/health)
- Fraud Prediction: `POST /api/predict_transaction`
- Compliance Query: `POST /api/query`

### Frontend (Streamlit)

```bash
cd ../frontend
streamlit run main.py
```

Configure secrets in `.streamlit/secrets.toml`:

```toml
backend_url = "http://localhost:8080"
API_KEY = "your-api-key"
```

## 🚀 Deployment on Google Cloud

### Step 1: Configure GCP

```bash
gcloud auth login
gcloud config set project risk-compliance-agent
gcloud app create
```

### Step 2: Deploy Backend

```bash
cd backend
gcloud app deploy
```

### Step 3: Deploy Frontend

```bash
cd ../frontend
gcloud app deploy
```

### Step 4: Verify

Open:

```
https://<your-project-id>.appspot.com/health
```

Response:

```json
{ "status": "ok" }
```

---

## 🔁 CI/CD Setup

- Use [Cloud Build](https://cloud.google.com/build) or GitHub Actions
- Optionally connect GitHub via Cloud Source Repositories
- Recommended: Use [Cloud Code](https://cloud.google.com/code/docs/vscode) in VS Code for integrated deployment

---

## 📚 Additional Resources

- [LangChain Docs](https://python.langchain.com/)
- [Google Cloud Logging](https://cloud.google.com/logging)
- [Vertex AI Gemini](https://cloud.google.com/vertex-ai/docs/generative-ai/overview)
- [BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/index.html)

---

## 🤝 Contributing

We welcome contributions! Please fork the repo and submit a pull request. For major changes, open an issue first to discuss your proposal.

```bash
git checkout -b feature/my-feature
git commit -am "Add new feature"
git push origin feature/my-feature
```

---

## 🪪 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🧾 Maintainer

**Javier Villacampa Porta**  
📧 `jvillacampaporta@deloitte.es`  
🌍 [LinkedIn](https://www.linkedin.com/in/javiervillacampaporta/)

---
