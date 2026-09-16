from groq import Groq
import logging
from app.core.config import settings


logger = logging.getLogger(__name__)
client = Groq(
    api_key=settings.groq_api_key
)


MODEL = "openai/gpt-oss-120b"


def generate_answer(
    question: str,
    context: str
) -> str:

    prompt = f"""
You are RepoLens, an AI codebase analysis assistant.

Rules:
1. Answer ONLY using the provided repository context.
2. Do not invent code, files, functions, classes, or behavior.
3. If the context is insufficient, say:
   "I could not determine this from the provided repository context."
4. Give a concise technical explanation.
5. Mention relevant file paths when useful.

Repository Context:
{context}

User Question:
{question}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise codebase analysis assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        return response.choices[0].message.content

    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        raise