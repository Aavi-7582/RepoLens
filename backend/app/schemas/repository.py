from pydantic import BaseModel, HttpUrl, field_validator


class RepositoryIngestRequest(BaseModel):
    repo_url: HttpUrl

    @field_validator("repo_url")
    @classmethod
    def must_be_github_url(cls, v: HttpUrl) -> HttpUrl:
        if v.host != "github.com":
            raise ValueError(
                "Only GitHub repository URLs are supported "
                "(e.g. https://github.com/owner/repository)"
            )
        parts = (v.path or "").strip("/").split("/")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(
                "Invalid GitHub repository URL. "
                "Expected format: https://github.com/owner/repository"
            )
        return v