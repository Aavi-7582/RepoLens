from sqlalchemy.orm import Session

from app.models.chunk import CodeChunk
from app.services.embeddings import generate_embedding


def retrieve_similar_chunks(
    db: Session,
    query: str,
    limit: int = 5
):
    query_embedding = generate_embedding(query)

    results = (
        db.query(CodeChunk)
        .order_by(
            CodeChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(limit)
        .all()
    )

    return results