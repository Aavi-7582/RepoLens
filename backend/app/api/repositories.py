from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.repository import RepositoryIngestRequest
from app.services.repository import parse_github_url
from app.services.github import GitHubService
from app.services.embeddings import generate_embedding
from app.services.file_filter import should_include_file
from app.models.chunk import CodeChunk
from app.services.retriever import retrieve_similar_chunks



from app.models import Repository, RepositoryFile
from app.services.chunker import chunk_code


router = APIRouter(
    prefix="/api/repositories",
    tags=["Repositories"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/ingest")
async def ingest_repository(
    request: RepositoryIngestRequest,
    db: Session = Depends(get_db)
):
    try:
        owner, repo = parse_github_url(
            str(request.repo_url)
        )

        github = GitHubService()

        repository_data = await github.get_repository(
            owner,
            repo
        )

        branch = repository_data["default_branch"]

        tree = await github.get_repository_tree(
            owner,
            repo,
            branch
        )

        existing = (
            db.query(Repository)
            .filter(
                Repository.full_name
                == repository_data["full_name"]
            )
            .first()
        )

        if existing:
            db.delete(existing)
            db.commit()

        repository = Repository(
            name=repository_data["name"],
            full_name=repository_data["full_name"],
            url=repository_data["html_url"],
            default_branch=branch
        )

        db.add(repository)
        db.commit()
        db.refresh(repository)

        files_added = 0

        for item in tree:

            if item["type"] != "blob":
                continue

            path = item["path"]

            if not should_include_file(path):
                continue

            try:
                content = await github.get_file_content(
                    owner,
                    repo,
                    path
                )

                file = RepositoryFile(
                    repository_id=repository.id,
                    file_path=path,
                    language=None,
                    content=content
                )

                db.add(file)
                db.flush()

                chunks = chunk_code(
                    path,
                    content
                )

                for chunk_data in chunks:
                    embedding = generate_embedding(
                        chunk_data["content"]
                    )

                    chunk = CodeChunk(
                        repository_id=repository.id,
                        file_id=file.id,
                        file_path=path,
                        language=chunk_data["language"],
                        chunk_type=chunk_data["chunk_type"],
                        symbol_name=chunk_data["symbol_name"],
                        content=chunk_data["content"],
                        embedding=embedding
                    )

                    db.add(chunk)
                    
                files_added += 1

            except Exception as e:
                import traceback
                with open("ingest_errors.log", "a") as f:
                    f.write(f"Error processing {path}: {e}\n{traceback.format_exc()}\n")
                continue

        db.commit()

        return {
            "message": "Repository ingested successfully",
            "repository": repository.full_name,
            "branch": branch,
            "files_added": files_added
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/search")
def search_repository(
    query: str,
    db: Session = Depends(get_db)
):
    results = retrieve_similar_chunks(
        db,
        query,
        limit=5
    )

    return [
        {
            "file_path": chunk.file_path,
            "symbol_name": chunk.symbol_name,
            "chunk_type": chunk.chunk_type,
            "language": chunk.language,
            "content": chunk.content
        }
        for chunk in results
    ]