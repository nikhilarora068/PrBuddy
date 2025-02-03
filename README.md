# 🤖 PR Buddy

### Overview

PR Buddy is a FastAPI-based webhook service designed to integrate with a GitHub App. It leverages OpenAI's GPT models to automatically generate and update pull request (PR) descriptions and reviews. When a PR is opened or updated, PR Bot fetches the details, generates an AI-driven summary and review, and updates the PR accordingly.

### Current Capabilities

PR Buddy currently offers the following powerful features to enhance your development workflow:

- **PR Summary Generation**: Automatically generates comprehensive summaries for your pull requests, ensuring all team members are on the same page.
- **PR Code Review**: Provides insightful code reviews powered by AI, helping to maintain code quality and consistency.
- **Inline Code Suggestions**: Offers intelligent inline code suggestions to improve your codebase and accelerate the review process.

## 🚀 Installation & Setup

### Prerequisites

- 🐍 Python 3.9+
- 🐙 [GitHub App](https://github.com/apps/pull-request-buddy) (with private key, app ID, and webhook URL configured)
- 🔑 OpenAI API Key

### Installation

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file inside the `app` folder and add the following variables:

   ```env
   GH_APP_PRIVATE_KEY="your_private_key"
   GH_APP_ID="your_app_id"
   GH_WEBHOOK_SECRET="your_secret"
   OPENAI_API_KEY="your_openai_key"
   GH_APP_AUTH_METHOD="APP"    # Use APP for GitHub app auth and PAT for access token auth
   GH_PAT="your_github_pat"
   ```

5. **Run the server**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
