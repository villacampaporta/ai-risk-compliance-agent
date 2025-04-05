FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# If you have a wheel file for Google agents, copy and install it here:
# COPY google_genai_agents-0.0.2.dev20250108-py3-none-any.whl ./
# RUN pip install --no-cache-dir google_genai_agents-0.0.2.dev20250108-py3-none-any.whl

ENV FLASK_ENV=production
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app", "-t", "500"]
