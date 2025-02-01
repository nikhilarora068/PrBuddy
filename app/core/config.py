from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Config(BaseSettings):
    GH_APP_PRIVATE_KEY: str = os.getenv("GH_APP_PRIVATE_KEY", "")
    GH_APP_ID: str = os.getenv("GH_APP_ID", "")

    GH_WEBHOOK_SECRET: str = os.getenv("GH_WEBHOOK_SECRET", "")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    GH_APP_AUTH_METHOD: str = os.getenv("GH_APP_AUTH_METHOD", "APP")

    GH_PAT: str = os.getenv("GH_PAT", "")


config = Config()
