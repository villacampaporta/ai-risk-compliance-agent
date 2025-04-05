import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    API_KEY = os.environ.get("API_KEY", "default-api-key")
    DEBUG = os.environ.get("DEBUG", "False") == "True"
