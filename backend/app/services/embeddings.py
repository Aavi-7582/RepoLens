from huggingface_hub import InferenceClient
from app.core.config import settings


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


client = InferenceClient(
    provider="hf-inference",
    api_key=settings.hf_token
)


def generate_embedding(text: str) -> list[float]:
    # Truncate text to avoid token limits on Hugging Face Inference API
    text = text[:2000]

    embedding = client.feature_extraction(
        text,
        model=EMBEDDING_MODEL
    )

    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()
        
    if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
        # Take the first vector if it returns a 2D array
        return embedding[0]
        
    return embedding