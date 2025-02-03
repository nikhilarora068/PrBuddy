import logging
import time
from openai import OpenAI
from app.core.config import config
from fastapi import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - [OpenAIClient] - %(message)s",
)
logger = logging.getLogger("OpenAIClient")


class OpenAIClient:
    """Handles OpenAI API calls for PR summaries and reviews."""

    def __init__(self):
        """Initialize OpenAI client with API key."""
        try:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize OpenAI client: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize OpenAI client"
            )

    def generate_text(self, prompt: str) -> str:
        """Generate text using OpenAI API."""
        if not prompt:
            logger.warning("Empty prompt provided to OpenAI API.")
            return "Error: Empty prompt provided."

        try:
            logger.info(f"Sending request to OpenAI: {prompt}")
            start_time = time.time()

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            execution_time = round(time.time() - start_time, 2)

            if response and response.choices:
                generated_text = response.choices[0].message.content
                logger.info(
                    f"OpenAI response received in {execution_time}s: {generated_text}"
                )
                return generated_text
            else:
                logger.warning("OpenAI response is empty.")
                raise HTTPException(status_code=500, detail="OpenAI response is empty.")

        except Exception as e:
            logger.exception(f"OpenAI API call failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to generate AI response"
            )


# Instantiate OpenAI API client
openai_client = OpenAIClient()
