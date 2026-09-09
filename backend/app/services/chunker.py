from pathlib import Path
from typing import List, Dict, Optional
from app.services.parser import extract_python_chunks
from app.services.embeddings import generate_embedding

# Document supported languages
SUPPORTED_PARSERS = {
    ".py": "python",
    # Add more as you implement parsers
}

# Document detection-only languages (no parser yet)
LANGUAGE_MAPPING = {
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

def detect_language(file_path: str) -> Optional[str]:
    """Detect language from file extension."""
    extension = Path(file_path).suffix.lower()
    return LANGUAGE_MAPPING.get(extension)

def chunk_code(file_path: str, content: str) -> List[Dict]:
    """
    Extract code chunks from file content.
    
    Returns:
        List of chunks with structure:
        {
            "chunk_type": "function_definition" | "class_definition" | "file",
            "symbol_name": str | None,
            "language": str | None,
            "content": str
        }
    """
    language = detect_language(file_path)
    
    # Unknown language
    if not language:
        return [{
            "chunk_type": "file",
            "symbol_name": None,
            "language": None,
            "content": content,
            "error": "Unknown file extension"
        }]
    
    # Supported parser: Python
    if language == "python":
        try:
            chunks = extract_python_chunks(content)
            
            # Fallback if no chunks extracted
            if not chunks:
                return [{
                    "chunk_type": "file",
                    "symbol_name": None,
                    "language": language,
                    "content": content,
                    "note": "No functions/classes found in file"
                }]
            
            # Return parsed chunks with language
            return [{**chunk, "language": language} for chunk in chunks]
            
        except Exception as e:
            # Graceful fallback on parse error
            return [{
                "chunk_type": "file",
                "symbol_name": None,
                "language": language,
                "content": content,
                "error": f"Parse error: {str(e)}"
            }]
    
    # Unsupported parser: Return whole file
    return [{
        "chunk_type": "file",
        "symbol_name": None,
        "language": language,
        "content": content,
        "note": f"Parser not implemented for {language}"
    }]