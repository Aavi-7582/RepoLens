from sqlalchemy.orm import Session

from app.services.retriever import retrieve_similar_chunks
from app.services.llm import generate_answer


def answer_question(
    db: Session,
    question: str,
    limit: int = 5
):

    chunks = retrieve_similar_chunks(
        db,
        question,
        limit
    )

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"""
File: {chunk.file_path}
Symbol: {chunk.symbol_name}
Language: {chunk.language}

Code:
{chunk.content}
"""
        )

    context = "\n---\n".join(context_parts)

    answer = generate_answer(
        question,
        context
    )

    sources = list({
        chunk.file_path
        for chunk in chunks
    })

    return {
        "answer": answer,
        "sources": sources
    }