from sqlalchemy.orm import Session

from app.models.chunk import CodeChunk
from app.services.embeddings import generate_embedding


def retrieve_similar_chunks(
    db: Session,
    query: str,
    repository_id: int,
    limit: int = 5
):
    query_embedding = generate_embedding(query)

    results = (
        db.query(CodeChunk)
        .filter(
            CodeChunk.repository_id == repository_id
        )
        .order_by(
            CodeChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
        .all()
    )

    seen_files = set()
    unique_results = []

    for chunk in results:
        if chunk.file_path in seen_files:
            continue

        seen_files.add(chunk.file_path)
        unique_results.append(chunk)

        if len(unique_results) == limit:
            break

    return unique_results