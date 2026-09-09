from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.groq_api_key
)


MODEL = "openai/gpt-oss-120b"


def generate_answer(
    question: str,
    context: str
) -> str:

    prompt = f"""
You are RepoLens, an AI codebase assistant.

Answer the user's question using ONLY the provided
repository context.

If the answer cannot be determined from the context,
say so clearly.

Do not invent files, functions, classes, or behavior.

Repository Context:
{context}

User Question:
{question}
"""

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