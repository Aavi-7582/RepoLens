from huggingface_hub import InferenceClient
from app.core.config import settings
import logging

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

client = InferenceClient(
    provider="hf-inference",
    api_key=settings.hf_token,
)

logger = logging.getLogger(__name__)


def generate_embedding(text: str) -> list[float]:
    try:
        # Truncate text to avoid token limits on Hugging Face Inference API
        text = text[:2000]

        embedding = client.feature_extraction(text, model=EMBEDDING_MODEL)

        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        # 2D array — take the first vector
        if (
            isinstance(embedding, list)
            and len(embedding) > 0
            and isinstance(embedding[0], list)
        ):
            return embedding[0]

        # 1D array — return as-is
        return embedding

    except Exception as exc:
        logger.error("Embedding generation failed: %s", exc)
        raise