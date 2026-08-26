from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cs",
    ".kt",
    ".swift",
    ".sql",
}


def should_include_file(path: str) -> bool:
    path_obj = Path(path)

    if any(
        directory in IGNORED_DIRECTORIES
        for directory in path_obj.parts
    ):
        return False

    if path_obj.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False

    return True