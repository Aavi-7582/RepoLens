from urllib.parse import urlparse


def parse_github_url(url: str):
    parsed = urlparse(url)

    if parsed.netloc != "github.com":
        raise ValueError("Only GitHub repositories are supported")

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    return owner, repo