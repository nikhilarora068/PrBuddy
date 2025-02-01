# Pull Request Buddy

### Overview

PRBuddy is a FastAPI-based webhook service designed to integrate with a GitHub App. It automatically generates and updates pull request (PR) descriptions and reviews using OpenAI's GPT models. When a PR is opened or updated, PRBuddy fetches the PR details, generates an AI-driven summary and review, and updates the PR accordingly.




## Installation & Setup

### Prerequisites

- Python 3.8+

- GitHub App (with private key, app ID, and webhook URL configured)

- OpenAI API Key

### Installation

1. Installing dependencies

```python
pip install -r requirements.txt
```
2. 
Running the server

```python
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```