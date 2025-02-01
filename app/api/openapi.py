from fastapi import APIRouter
from app.services.openapi_client import openai_client

openapi_router = APIRouter()

@openapi_router.get("/generate-text")
def generate_text():
    prompt = "What is the meaning of life?"
    response = openai_client.generate_text(prompt)
    return {"response": response}
