import jwt
import time
import httpx
from app.core.config import config


class InstallationToken:
    def __init__(self):
        # self.PRIVATE_KEY_PATH = config.GITHUB_APP_PRIVATE_KEY_PATH
        self.APP_ID = config.GH_APP_ID
        self.PRIVATE_KEY = config.GH_APP_PRIVATE_KEY
        # with open(self.PRIVATE_KEY_PATH, "r") as f:
            # self.PRIVATE_KEY = f.read()

    def generate_jwt(self):
        now = int(time.time())
        payload = {
            "iat": now,  # Issued at
            "exp": now + (10 * 60),  # Expiry (10 minutes)
            "iss": self.APP_ID  # GitHub App ID
        }
        encoded_jwt = jwt.encode(payload, self.PRIVATE_KEY, algorithm="RS256")
        return encoded_jwt

    @staticmethod
    def get_installation_id(jwt_token):
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        response = httpx.get("https://api.github.com/app/installations", headers=headers)
        response.raise_for_status()
        installations = response.json()
        return installations[0]["id"]  # Assuming first installation

    @staticmethod
    def get_installation_token(installation_id, jwt_token):
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        response = httpx.post(url, headers=headers)
        response.raise_for_status()
        return {"token" : response.json()["token"]}

    def get_installation_token_main(self):
        jwt_token = self.generate_jwt()
        installation_id = self.get_installation_id(jwt_token)
        installation_token = self.get_installation_token(installation_id, jwt_token)
        return installation_token

installationToken = InstallationToken()

