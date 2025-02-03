import logging
import json
from fastapi import APIRouter, Request, HTTPException
from app.services.webhook import webhook

webhook_router = APIRouter()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - [Router] - %(message)s",
)
logger = logging.getLogger("Router")


@webhook_router.post("")
async def handle_webhook(request: Request):
    """Handles incoming GitHub PR webhooks."""
    try:
        payload_raw = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")

        if not webhook.verify_signature(signature, payload_raw):
            logger.warning("Invalid webhook signature received.")
            raise HTTPException(status_code=403, detail="Invalid signature")

        payload = json.loads(payload_raw)
        response = await webhook.handle_pr_event(payload)
        return response
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except HTTPException as e:
        logger.error(f"HTTP Exception in webhook handler: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error in webhook handler: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
