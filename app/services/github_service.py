from fastapi import APIRouter, HTTPException
from ..schema import FileChange, PRFilesResponse, ExpandedFile, AllFilesContentResponse
import requests, os
import base64
from ..utils import fetch_file_content


router = APIRouter(prefix="/github", tags=["github"])


@router.get("/fetch_pr_files", response_model=PRFilesResponse)
async def fetch_pr_files(owner: str, repo: str, pr_number: int):
    """
    Fetches list of changed files in a PR, including:
    - filename
    - status
    - patch (diff)
    - contents_url (for fetching full file content)
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error: {response.text}"
        )

    raw_files = response.json()
    cleaned_files = []

    for f in raw_files:
        cleaned_files.append(
            FileChange(
                filename=f["filename"],              # always present
                status=f["status"],                  # always present
                patch=f.get("patch"),                # optional
                contents_url=f.get("contents_url")   # optional
            )
        )

    return PRFilesResponse(files=cleaned_files)

@router.get("/fetch_all_file_contents", response_model=AllFilesContentResponse)
async def fetch_all_file_contents(owner: str, repo: str, pr_number: int):
    """
    Fetches full decoded contents for all changed files in a PR.
    Combines:
    - filename
    - patch
    - full decoded content (if available)
    """

    # 1. Get PR file metadata first
    pr_files_response = await fetch_pr_files(owner, repo, pr_number)
    files = pr_files_response.files

    expanded_files = []

    for file in files:

        if not file.contents_url:  # Skip removed files
            expanded_files.append(
                ExpandedFile(
                    filename=file.filename,
                    patch=file.patch,
                    content=None
                )
            )
            continue
        
        # 2. Fetch full file content
        file_content_data = fetch_file_content(file.contents_url)

        expanded_files.append(
            ExpandedFile(
                filename=file.filename,
                patch=file.patch,
                content=file_content_data.get("file_content")
            )
        )

    return AllFilesContentResponse(files=expanded_files)

