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

    return results