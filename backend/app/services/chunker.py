from pathlib import Path

from app.services.parser import extract_python_chunks


def detect_language(file_path: str):
    extension = Path(file_path).suffix.lower()

    mapping = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
    }

    return mapping.get(extension)


def chunk_code(
    file_path: str,
    content: str
):
    language = detect_language(file_path)

    if language == "python":
        chunks = extract_python_chunks(content)

        return [
            {
                **chunk,
                "language": language
            }
            for chunk in chunks
        ]

    return [
        {
            "chunk_type": "file",
            "symbol_name": None,
            "language": language,
            "content": content
        }
    ]