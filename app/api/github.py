from fastapi import APIRouter
from app.services.github_client import github_client

github_router = APIRouter()


OWNER="nikhilarora068"
REPO_FULL_NAME="nikhilarora068/PrBuddy"
PR_NUMBER=6
summary = "This is a dummy summary"
review_comment = "This is a dummy comment"

@github_router.get("/get-repo-details")
async def get_repo_details():
    repo = await github_client.get_repo(REPO_FULL_NAME)
    return {"repo_details": repo.raw_data}

@github_router.get("/get-pr-details")
async def get_pr_details():
    pr = await github_client.get_pr_details(REPO_FULL_NAME, PR_NUMBER)
    return {"pr_details": pr.raw_data}

@github_router.get("/get-pr-diff")
async def get_pr_diff():
    diff = await github_client.get_pr_diff(REPO_FULL_NAME, PR_NUMBER)
    return {"pr_diff": diff}

@github_router.get("/update-pr-description")
async def update_pr_description():
    response = await github_client.update_pr_description(REPO_FULL_NAME, PR_NUMBER, summary)
    return {"update_response": response}

@github_router.get("/update-pr-comment")
async def update_pr_comment():
    response = await github_client.add_pr_comment(REPO_FULL_NAME, PR_NUMBER, review_comment)
    return {"comment_response": response}

