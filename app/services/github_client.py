import logging
import httpx
from fastapi import HTTPException
from github import Github, GithubIntegration
from app.services.installation_token import installationToken
from app.core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - [GitHubAPIClient] - %(message)s",
)
logger = logging.getLogger("GitHubAPIClient")


class GitHubAPIClient:
    """Handles GitHub API authentication and requests using either PAT or GitHub App."""

    def __init__(self):
        """Initialize GitHub API client"""
        try:
            self.auth_headers = installationToken.get_installation_token_main()
            logger.info("GitHub API client initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize GitHub API client: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to initialize GitHub API client"
            )

    @staticmethod
    async def get_github_client_using_pat():
        return Github(config.GH_PAT)

    @staticmethod
    async def get_github_client_using_app():
        """
        Authenticate as a GitHub App and retrieve an installation client.
        """
        try:
            jwt_token = installationToken.generate_jwt()
            installation_id = installationToken.get_installation_id(jwt_token)
            integration = GithubIntegration(
                installationToken.APP_ID,
                installationToken.PRIVATE_KEY.replace("\\n", "\n"),
            )
            access_token = integration.get_access_token(installation_id).token
            return Github(access_token)
        except Exception as e:
            logger.error(f"Failed to authenticate GitHub App: {str(e)}")
            raise HTTPException(status_code=500, detail="GitHub authentication failed")

    async def get_github_client(self):
        """
        Get the GitHub client based on the authentication method.
        """
        if config.GH_APP_AUTH_METHOD == "APP":
            return await self.get_github_client_using_app()
        else:
            return await self.get_github_client_using_pat()

    async def get_repo(self, repo_full_name: str):
        """Fetch repository details."""
        try:
            github = await self.get_github_client()
            repo = github.get_repo(repo_full_name)
            logger.info(f"Fetched repository details: {repo_full_name}")
            return repo
        except Exception as e:
            logger.error(f"Error fetching repository {repo_full_name}: {str(e)}")
            raise HTTPException(status_code=404, detail="Repository not found")

    async def get_pr_details(self, repo_full_name: str, pr_number: int):
        """Fetch Pull Request details."""
        try:
            github = await self.get_github_client()
            repo = github.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            logger.info(f"Fetched PR #{pr_number} from {repo_full_name}")
            return pr
        except Exception as e:
            logger.error(
                f"Error fetching PR #{pr_number} from {repo_full_name}: {str(e)}"
            )
            raise HTTPException(status_code=404, detail="Pull request not found")

    async def get_pr_diff(self, repo_full_name: str, pr_number: int):
        """Fetch the diff of a pull request."""
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        headers = {**self.auth_headers, "Accept": "application/vnd.github.v3.diff"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                logger.info(f"Fetched diff for PR #{pr_number} from {repo_full_name}")
                return response.text
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error while fetching PR diff: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code, detail="Failed to fetch PR diff"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching PR diff: {str(e)}")
            raise HTTPException(status_code=500, detail="Error fetching PR diff")

    async def update_pr_description(
        self, repo_full_name: str, pr_number: int, description: str
    ):
        """Update the pull request description."""
        try:
            github = await self.get_github_client()
            repo = github.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.edit(body=description)
            logger.info(f"Updated PR #{pr_number} description in {repo_full_name}")
            return {"message": "PR description updated", "url": pr.html_url}
        except Exception as e:
            logger.error(f"Error updating PR description: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Failed to update PR description"
            )

    async def add_pr_comment(self, repo_full_name: str, pr_number: int, comment: str):
        """Add a review comment to the PR."""
        try:
            github = await self.get_github_client()
            repo = github.get_repo(repo_full_name)
            issue = repo.get_issue(pr_number)
            issue.create_comment(comment)
            logger.info(f"Added comment to PR #{pr_number} in {repo_full_name}")
            return {"message": "Comment added", "url": issue.html_url}
        except Exception as e:
            logger.error(f"Error adding PR comment: {str(e)}")
            raise HTTPException(status_code=400, detail="Failed to add comment to PR")


# Instantiate the client
github_client = GitHubAPIClient()
