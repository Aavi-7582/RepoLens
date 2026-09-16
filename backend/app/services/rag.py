import logging

from sqlalchemy.orm import Session

from app.services.retriever import retrieve_similar_chunks
from app.services.llm import generate_answer

logger = logging.getLogger(__name__)

# Target fallback string used to detect unanswerable queries
FALLBACK_TRIGGER = "I could not determine this from the provided repository context."


def answer_question(
    db: Session,
    question: str,
    repository_id: int,
    limit: int = 5,
):
    chunks = retrieve_similar_chunks(db, question, repository_id, limit)

    if not chunks:
        logger.info(
            "No relevant chunks found for repository_id=%s — returning empty result",
            repository_id,
        )
        return {
            "answer": "I could not find relevant information in the repository.",
            "sources": [],
        }

    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"""
SOURCE {i}
File: {chunk.file_path}
Symbol: {chunk.symbol_name or "N/A"}
Language: {chunk.language or "N/A"}

Code:
{chunk.content}
"""
        )

    context = "\n---\n".join(context_parts)

    answer = generate_answer(question, context)

    # If the LLM indicates it couldn't find the answer in the context, return an empty sources list
    if FALLBACK_TRIGGER.lower() in answer.lower():
        logger.info(
            "RAG fallback triggered for repository_id=%s — LLM could not determine answer from context",
            repository_id,
        )
        return {
            "answer": answer,
            "sources": [],
        }

    sources = [
        {
            "file": chunk.file_path,
            "symbol": chunk.symbol_name,
            "language": chunk.language,
        }
        for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }