from fastapi import FastAPI

from src.config import PROJECT_NAME


# Create app
app: FastAPI = FastAPI(title=PROJECT_NAME)
