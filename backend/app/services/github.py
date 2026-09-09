import httpx

from app.core.config import settings


class GitHubService:

    BASE_URL = "https://api.github.com"

    async def get_repository(self, owner: str, repo: str):
        headers = {
            "Accept": "application/vnd.github+json"
        }

        if settings.github_token:
            headers["Authorization"] = (
                f"Bearer {settings.github_token}"
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=headers
            )

        response.raise_for_status()

        return response.json()

    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str
    ):
        headers = {
            "Accept": "application/vnd.github+json"
        }

        if settings.github_token:
            headers["Authorization"] = (
                f"Bearer {settings.github_token}"
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/"
                f"{owner}/{repo}/git/trees/{branch}",
                params={"recursive": "1"},
                headers=headers
            )

        response.raise_for_status()

        return response.json()["tree"]

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str
    ):
        headers = {
            "Accept": "application/vnd.github.v3.raw"
        }

        if settings.github_token:
            headers["Authorization"] = (
                f"Bearer {settings.github_token}"
            )

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/"
                f"{owner}/{repo}/contents/{path}",
                headers=headers
            )

        response.raise_for_status()

        return response.text