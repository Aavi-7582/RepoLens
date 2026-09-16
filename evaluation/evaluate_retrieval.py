import json
import sys
from pathlib import Path

# Allow importing backend modules
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR / "backend"))

from app.core.database import SessionLocal
from app.services.retriever import retrieve_similar_chunks


DATASET_PATH = Path(__file__).parent / "dataset.json"

# Change this after identifying the repository ID in your database.
REPOSITORY_ID = 1

TOP_K_VALUES = [1, 3, 5]


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def file_matches(actual_file, expected_files):
    actual_file = actual_file.replace("\\", "/")

    return any(
        actual_file == expected
        or actual_file.endswith("/" + expected)
        for expected in expected_files
    )


def evaluate():
    dataset = load_dataset()

    db = SessionLocal()

    results = {
        k: 0
        for k in TOP_K_VALUES
    }

    try:
        for index, item in enumerate(dataset, start=1):
            question = item["question"]
            expected_files = item["expected_files"]

            chunks = retrieve_similar_chunks(
                db=db,
                query=question,
                repository_id=REPOSITORY_ID,
                limit=max(TOP_K_VALUES)
            )

            retrieved_files = [
                chunk.file_path
                for chunk in chunks
            ]

            print(f"\n[{index}/{len(dataset)}] {question}")
            print(f"Expected: {expected_files}")
            print(f"Retrieved: {retrieved_files}")

            for k in TOP_K_VALUES:
                top_k_files = retrieved_files[:k]

                hit = any(
                    file_matches(file, expected_files)
                    for file in top_k_files
                )

                if hit:
                    results[k] += 1

        print("\n" + "=" * 50)
        print("RETRIEVAL EVALUATION")
        print("=" * 50)

        total = len(dataset)

        for k in TOP_K_VALUES:
            score = results[k] / total
            print(
                f"Hit@{k}: "
                f"{results[k]}/{total} "
                f"({score:.2%})"
            )

    finally:
        db.close()


if __name__ == "__main__":
    evaluate()