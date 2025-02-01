import logging
import hmac
import hashlib
from fastapi import HTTPException
from app.core.config import config
from app.services.github_client import github_client

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - [WebhookHandler] - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("WebhookHandler")


class WebhookHandler:
    """Handles incoming GitHub webhooks for PR events."""

    def __init__(self):
        try:
            self.webhook_secret = config.GH_WEBHOOK_SECRET
            logger.info("Webhook handler initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize webhook handler: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize webhook handler"
            )

    def verify_signature(self, signature: str, payload: bytes) -> bool:
        """Verifies the GitHub webhook signature."""
        if not self.webhook_secret:
            logger.warning("Webhook secret not set. Skipping signature verification.")
            return (
                True  # Skip verification if no secret is set (useful for local testing)
            )

        try:
            mac = hmac.new(self.webhook_secret.encode(), payload, hashlib.sha256)
            expected_signature = f"sha256={mac.hexdigest()}"
            is_valid = hmac.compare_digest(expected_signature, signature or "")
            if is_valid:
                logger.info("Webhook signature verification successful.")
            else:
                logger.warning("Webhook signature verification failed.")
            return is_valid
        except Exception as e:
            logger.exception(
                f"Exception occurred during webhook signature verification: {str(e)}"
            )
            return False

    @staticmethod
    async def handle_pr_event(payload: dict):
        """Processes the pull request event."""
        try:
            pr_action = payload.get("action")
            repo_full_name = payload.get("repository", {}).get("full_name")
            pr_number = payload.get("pull_request", {}).get("number")
            pr_diff_url = payload.get("pull_request", {}).get("diff_url")

            if not repo_full_name or not pr_number:
                logger.error("Missing required fields in payload.")
                raise HTTPException(status_code=400, detail="Invalid payload structure")

            logger.info(
                f"Received PR event: action={pr_action}, repo={repo_full_name}, PR=#{pr_number}"
            )

            if pr_action not in ["opened", "synchronize"]:
                logger.info(f"Ignored PR action: {pr_action}")
                return {"message": f"Ignored PR action: {pr_action}"}

            logger.info(
                f"Processing PR event for repository '{repo_full_name}' PR #{pr_number}"
            )
            logger.info(f"PR diff URL: {pr_diff_url}")

            summary = "This is a dummy summary"
            review_comment = "This is a dummy comment"

            # Update PR description
            logger.info(f"Updating PR description for {repo_full_name} PR #{pr_number}")
            update_response = await github_client.update_pr_description(
                repo_full_name, pr_number, summary
            )
            logger.info(f"PR description updated successfully: {update_response}")

            # Add a review comment to the PR
            logger.info(f"Adding review comment to PR #{pr_number} in {repo_full_name}")
            comment_response = await github_client.add_pr_comment(
                repo_full_name, pr_number, review_comment
            )
            logger.info(f"PR comment added successfully: {comment_response}")

            return {
                "summary_update": update_response,
                "comment_response": comment_response,
            }

        except HTTPException as e:
            logger.error(f"HTTP Exception in handle_pr_event: {e.detail}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error occurred in handle_pr_event: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


webhook = WebhookHandler()
