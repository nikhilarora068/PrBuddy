from fastapi import APIRouter
from app.services.github_client import github_client

github_router = APIRouter()


DUMMY_SUMMARY = "This is a dummy summary"
DUMMY_COMMENT = "This is a dummy comment"

@github_router.get("/get-repo-details")
async def get_repo_details(repo_name: str):
    repo = await github_client.get_repo(repo_name)
    return {"repo_details": repo.raw_data}

@github_router.get("/get-pr-details")
async def get_pr_details(repo_name: str, pr_number: int):
    pr = await github_client.get_pr_details(repo_name, pr_number)
    return {"pr_details": pr.raw_data}

@github_router.get("/get-pr-diff")
async def get_pr_diff(repo_name: str, pr_number: int):
    diff = await github_client.get_pr_diff(repo_name, pr_number)
    return {"pr_diff": diff}

@github_router.get("/update-pr-description")
async def update_pr_description(repo_name: str, pr_number: int):
    response = await github_client.update_pr_description(repo_name, pr_number, DUMMY_SUMMARY)
    return {"update_response": response}

@github_router.get("/add-pr-comment")
async def add_pr_comment(repo_name: str, pr_number: int):
    response = await github_client.add_pr_comment(repo_name, pr_number, DUMMY_COMMENT)
    return {"comment_response": response}

