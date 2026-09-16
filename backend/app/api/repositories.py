import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Repository, RepositoryFile
from app.models.chunk import CodeChunk
from app.schemas.repository import RepositoryIngestRequest
from app.services.chunker import chunk_code
from app.services.embeddings import generate_embedding
from app.services.file_filter import should_include_file
from app.services.github import GitHubService
from app.services.rag import answer_question
from app.services.repository import parse_github_url
from app.services.retriever import retrieve_similar_chunks

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"],
)


# ---------------------------------------------------------------------------
# POST /api/repositories/ingest
# ---------------------------------------------------------------------------

@router.post("/ingest")
async def ingest_repository(
    request: RepositoryIngestRequest,
    db: Session = Depends(get_db),
):
    """
    Ingest a GitHub repository.

    - 200: Repository already cached — no work done.
    - 201: New repository successfully ingested.
    - 400: Invalid GitHub URL (caught by Pydantic schema validator before this).
    - 404: GitHub repository does not exist.
    - 502: GitHub API communication failure.
    - 500: Unexpected internal error.
    """
    raw_url = str(request.repo_url)

    # parse_github_url validates the URL structure (non-GitHub raises ValueError)
    try:
        owner, repo = parse_github_url(raw_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    github = GitHubService()

    # ------------------------------------------------------------------
    # Fetch repository metadata from GitHub
    # ------------------------------------------------------------------
    try:
        repository_data = await github.get_repository(owner, repo)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.warning("GitHub repository not found: %s/%s", owner, repo)
            raise HTTPException(
                status_code=404,
                detail=f"GitHub repository '{owner}/{repo}' does not exist or is private.",
            )
        logger.error(
            "GitHub API error while fetching %s/%s — HTTP %s",
            owner,
            repo,
            exc.response.status_code,
        )
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with GitHub. Please try again later.",
        )
    except httpx.RequestError as exc:
        logger.error("GitHub request error for %s/%s: %s", owner, repo, type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with GitHub. Please try again later.",
        )

    branch = repository_data["default_branch"]

    # ------------------------------------------------------------------
    # Cache check — return early if already ingested
    # ------------------------------------------------------------------
    try:
        existing = (
            db.query(Repository)
            .filter(Repository.full_name == repository_data["full_name"])
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Database error while checking for existing repository")
        raise HTTPException(status_code=500, detail="A database error occurred.")

    if existing:
        logger.info(
            "Repository already ingested — returning cached result: %s (id=%s)",
            existing.full_name,
            existing.id,
        )
        return JSONResponse(
            status_code=200,
            content={
                "message": "Repository already ingested. Using existing repository context.",
                "repository_id": existing.id,
                "repository": existing.full_name,
                "cached": True,
            },
        )

    # ------------------------------------------------------------------
    # Fetch repository tree
    # ------------------------------------------------------------------
    try:
        tree = await github.get_repository_tree(owner, repo, branch)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "GitHub API error while fetching tree for %s/%s — HTTP %s",
            owner,
            repo,
            exc.response.status_code,
        )
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with GitHub. Please try again later.",
        )
    except httpx.RequestError as exc:
        logger.error(
            "GitHub request error while fetching tree for %s/%s: %s",
            owner,
            repo,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with GitHub. Please try again later.",
        )

    # ------------------------------------------------------------------
    # Create repository record
    # ------------------------------------------------------------------
    try:
        repository = Repository(
            name=repository_data["name"],
            full_name=repository_data["full_name"],
            url=repository_data["html_url"],
            default_branch=branch,
        )
        db.add(repository)
        db.commit()
        db.refresh(repository)
    except SQLAlchemyError:
        logger.exception("Database error while creating repository record for %s/%s", owner, repo)
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred.")

    logger.info(
        "Starting ingestion for %s (id=%s), branch=%s",
        repository.full_name,
        repository.id,
        branch,
    )

    # ------------------------------------------------------------------
    # Ingest files
    # ------------------------------------------------------------------
    files_added = 0

    for item in tree:
        if item["type"] != "blob":
            continue

        path = item["path"]

        if not should_include_file(path):
            continue

        try:
            content = await github.get_file_content(owner, repo, path)

            file = RepositoryFile(
                repository_id=repository.id,
                file_path=path,
                language=None,
                content=content,
            )
            db.add(file)
            db.flush()

            chunks = chunk_code(path, content)

            for chunk_data in chunks:
                embedding = generate_embedding(chunk_data["content"])

                chunk = CodeChunk(
                    repository_id=repository.id,
                    file_id=file.id,
                    file_path=path,
                    language=chunk_data["language"],
                    chunk_type=chunk_data["chunk_type"],
                    symbol_name=chunk_data["symbol_name"],
                    content=chunk_data["content"],
                    embedding=embedding,
                )
                db.add(chunk)

            files_added += 1

        except Exception:
            logger.exception("Failed to process file %s — skipping", path)
            continue

    try:
        db.commit()
    except SQLAlchemyError:
        logger.exception(
            "Database commit failed after ingesting %s/%s", owner, repo
        )
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred.")

    logger.info(
        "Ingestion complete for %s (id=%s) — %s files added",
        repository.full_name,
        repository.id,
        files_added,
    )

    return JSONResponse(
        status_code=201,
        content={
            "message": "Repository ingested successfully",
            "repository_id": repository.id,
            "repository": repository.full_name,
            "branch": branch,
            "files_added": files_added,
            "cached": False,
        },
    )


# ---------------------------------------------------------------------------
# GET /api/repositories/search
# ---------------------------------------------------------------------------

@router.get("/search")
def search_repository(
    query: str,
    repository_id: int,
    db: Session = Depends(get_db),
):
    results = retrieve_similar_chunks(db, query, repository_id, limit=5)

    return [
        {
            "file_path": chunk.file_path,
            "symbol_name": chunk.symbol_name,
            "chunk_type": chunk.chunk_type,
            "language": chunk.language,
            "content": chunk.content,
        }
        for chunk in results
    ]


# ---------------------------------------------------------------------------
# GET /api/repositories/ask
# ---------------------------------------------------------------------------

@router.get("/ask")
def ask_repository(
    query: str = Query(..., description="Question to ask about the repository"),
    repository_id: int = Query(..., description="ID of the ingested repository"),
    db: Session = Depends(get_db),
):
    """
    Answer a question about an ingested repository using RAG.

    - 200: Successful RAG response.
    - 400: Invalid query or repository_id.
    - 404: Repository does not exist.
    - 502: External embedding/LLM API failure.
    - 500: Unexpected internal error.
    """
    # Validate query
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    # Validate repository_id
    if repository_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="repository_id must be a positive integer.",
        )

    # Verify repository exists
    try:
        repo = db.query(Repository).filter(Repository.id == repository_id).first()
    except SQLAlchemyError:
        logger.exception("Database error while looking up repository_id=%s", repository_id)
        raise HTTPException(status_code=500, detail="A database error occurred.")

    if repo is None:
        raise HTTPException(
            status_code=404,
            detail=f"Repository with id={repository_id} does not exist.",
        )

    # Run RAG pipeline
    try:
        result = answer_question(db, query, repository_id)
    except Exception as exc:
        # Distinguish external API failures from unexpected errors
        exc_type = type(exc).__name__
        if any(
            marker in exc_type.lower()
            for marker in ("httpstatus", "request", "groq", "inference", "huggingface")
        ):
            logger.error(
                "External API failure during RAG for repository_id=%s: %s",
                repository_id,
                exc_type,
            )
            raise HTTPException(
                status_code=502,
                detail="An external API (embedding or LLM) is currently unavailable.",
            )

        logger.exception(
            "Unexpected error during RAG for repository_id=%s", repository_id
        )
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    return result