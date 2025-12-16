from fastapi import APIRouter
from ..schema import FileChange, PRFilesResponse
import requests
import os
import base64


router = APIRouter(prefix="/github", tags=["github"])


@router.get("/fetch_pr_files", response_model=PRFilesResponse)
async def fetch_pr_files(owner: str, repo: str, pr_number: int):
    """
    Fetches list of changed files in a PR, including:
    - filename
    - status
    - patch (diff)
    - contents_url (where to fetch full file content)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {response.text}")

    raw_files = response.json()

    cleaned_files = []

    for f in raw_files:
        # Skip removed or binary files (no contents_url)
        contents_url = f.get("contents_url")
        patch = f.get("patch")

        cleaned_files.append(
            FileChange(
                filename=f["filename"],  # Always present hence no get()
                status=f["status"],
                patch=patch,
                contents_url=contents_url
            )
        )

    return PRFilesResponse(files=cleaned_files)
