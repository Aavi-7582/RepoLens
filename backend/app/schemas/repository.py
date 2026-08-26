from pydantic import BaseModel, HttpUrl


class RepositoryIngestRequest(BaseModel):
    repo_url: HttpUrl