import logging
import hmac
import hashlib
import json
from fastapi import HTTPException
from app.core.config import config
from app.services.github_client import github_client
from app.services.openai_client import openai_client
from app.core.pr_summary_prompt import PR_SUMMARY_PROMPT
from app.core.pr_review_prompt import PR_REVIEW_PROMPT
from app.core.pr_inline_fix_prompt import PR_INLINE_FIX_PROMPT

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

    async def get_pr_diff(self, repo_full_name: str, pr_number: int) -> str:
        """Fetches the diff of a pull request."""
        logger.info(f"Fetching PR diff for PR #{pr_number}")
        pr_diff = await github_client.get_pr_diff(repo_full_name, pr_number)
        logger.info(f"Fetched PR diff for PR #{pr_number}")
        return pr_diff

    async def generate_pr_summary(self, pr_diff: str) -> str:
        """Generates a summary of the PR changes."""
        logger.info("Generating PR summary")
        summary = openai_client.generate_text(PR_SUMMARY_PROMPT.format(pr_diff=pr_diff))
        logger.info(f"Generated PR summary: {summary}")
        return summary

    async def generate_pr_review(self, pr_diff: str) -> str:
        """Generates a review of the PR changes."""
        logger.info("Generating PR review")
        review = openai_client.generate_text(PR_REVIEW_PROMPT.format(pr_diff=pr_diff))
        logger.info(f"Generated PR review: {review}")
        return review

    async def generate_inline_suggestions(self, pr_diff: str) -> list:
        """Generates inline suggestions for the PR changes."""
        logger.info("Generating inline suggestions")
        inline_suggestions = openai_client.generate_text(
            PR_INLINE_FIX_PROMPT.format(pr_diff=pr_diff)
        )
        logger.info(f"Generated inline suggestions: {inline_suggestions}")

        # Remove Markdown formatting
        cleaned_json = inline_suggestions.strip("```json").strip("```").strip()
        logger.debug(f"Cleaned JSON: {cleaned_json}")

        # Convert to Python list of dictionaries
        suggestions = json.loads(cleaned_json)
        return suggestions

    async def update_pr_description(
        self, repo_full_name: str, pr_number: int, summary: str
    ) -> dict:
        """Updates the description of a pull request."""
        logger.info(f"Updating PR description for PR #{pr_number}")
        response = await github_client.update_pr_description(
            repo_full_name, pr_number, summary
        )
        logger.info(f"Updated PR description for PR #{pr_number}")
        return response

    async def add_pr_review(self, repo_full_name: str, pr_number: int, review: str):
        """Add a review comment to the PR."""
        logger.info(f"Adding review comment to PR #{pr_number} in {repo_full_name}")
        response = await github_client.add_pr_comment(repo_full_name, pr_number, review)
        logger.info(f"PR comment added successfully: {response}")
        return response

    async def add_inline_suggestions(
        self,
        repo_full_name: str,
        pr_number: int,
        inline_suggestions: list,
    ):
        """Add inline suggestions to a PR."""
        logger.info(f"Adding inline suggestions to PR #{pr_number} in {repo_full_name}")
        response = {}
        for suggestion in inline_suggestions:
            if not all(k in suggestion for k in ["file_path", "line", "suggestion"]):
                logger.warning(f"Skipping invalid suggestion: {suggestion}")
                continue

            logger.info(
                f"Adding inline suggestion to {suggestion['file_path']}:{suggestion['line']}"
            )
            response = await github_client.add_inline_suggestion(
                repo_full_name,
                pr_number,
                suggestion["file_path"],
                int(suggestion["line"]),
                suggestion["suggestion"],
            )
            logger.info(
                f"Added inline suggestion to {suggestion['file_path']}:{suggestion['line']}"
            )
        logger.info(f"Inline suggestions added to PR #{pr_number}")
        return response

    async def handle_pr_event(self, payload: dict):
        """Processes the pull request event."""
        try:
            pr_action = payload.get("action")
            repo_full_name = payload.get("repository", {}).get("full_name")
            pr_number = payload.get("pull_request", {}).get("number")

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
                f"Processing PR event '{pr_action}' for repository '{repo_full_name}' PR #{pr_number}"
            )

            # pr_diff = await self.get_pr_diff(repo_full_name, pr_number)
            # summary = await self.generate_pr_summary(pr_diff)
            # review = await self.generate_pr_review(pr_diff)

            summary = "This is a dummy summary"
            review = "This is a dummy review"

            update_pr_summary_response = await self.update_pr_description(
                repo_full_name, pr_number, summary
            )
            add_pr_review_comment_response = await self.add_pr_review(
                repo_full_name, pr_number, review
            )

            # inline_suggestions = await self.generate_inline_suggestions(pr_diff)
            # add_inline_suggestion_response = await self.add_inline_suggestions(
            #     repo_full_name, pr_number, inline_suggestions
            # )

            return {
                "summary_respone": update_pr_summary_response,
                "review_response": add_pr_review_comment_response,
                # "inline_suggestions_response": add_inline_suggestion_response,
            }

        except HTTPException as e:
            logger.error(f"HTTP Exception in handle_pr_event: {e.detail}")
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error occurred in handle_pr_event: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


webhook = WebhookHandler()
