from fastapi import FastAPI
from app.api.health import health_router
from app.api.github import github_router
from app.api.openapi import openapi_router
from app.api.webhook import webhook_router

app = FastAPI()

# Register Routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(github_router, prefix="/github", tags=["GitHub"])
app.include_router(openapi_router, prefix="/openai", tags=["OpenAI"])
app.include_router(webhook_router, prefix="/webhook", tags=["Webhook"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
