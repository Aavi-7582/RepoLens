import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubService:

    BASE_URL = "https://api.github.com"

    def _auth_headers(self, accept: str = "application/vnd.github+json") -> dict:
        headers = {"Accept": accept}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    async def get_repository(self, owner: str, repo: str) -> dict:
        logger.info("Fetching GitHub repository metadata: %s/%s", owner, repo)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self._auth_headers(),
            )

        if response.status_code == 404:
            logger.warning("GitHub repository not found: %s/%s", owner, repo)
            raise httpx.HTTPStatusError(
                "Repository not found",
                request=response.request,
                response=response,
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "GitHub API error for %s/%s — HTTP %s",
                owner,
                repo,
                response.status_code,
            )
            raise

        return response.json()

    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list:
        logger.info("Fetching repository tree: %s/%s @ %s", owner, repo, branch)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}",
                params={"recursive": "1"},
                headers=self._auth_headers(),
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "Failed to fetch tree for %s/%s — HTTP %s",
                owner,
                repo,
                response.status_code,
            )
            raise

        return response.json()["tree"]

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                headers=self._auth_headers(accept="application/vnd.github.v3.raw"),
            )

        response.raise_for_status()

        return response.text