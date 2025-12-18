from fastapi import HTTPException
from ..schema import *
import requests, os
from ..utils import fetch_file_content



def fetch_repo_tree(owner: str, repo: str, branch: str = "main"):

    """
    Fetches the repository tree for a given branch.
    """
    # Get the reference for the branch to find the latest commit
    ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    ref_response = requests.get(url=ref_url, headers=headers)
    if ref_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error (ref): {ref_response.text}"
        )
    
    ref_data = ref_response.json()


    # Get the commit URL from the ref data
    commit_url = ref_data["object"]["url"]
    commit_response = requests.get(url=commit_url, headers=headers)
    if commit_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error (commit): {commit_response.text}"
        )
    commit_data = commit_response.json()

    # Get the tree URL from the commit data
    tree_url = commit_data["tree"]["url"] + "?recursive=1"
    tree_response = requests.get(url=tree_url, headers=headers)
    if tree_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error (tree): {tree_response.text}"
        )

    tree_data = tree_response.json()

    tree_items = []
    for item in tree_data.get("tree", []):
        tree_items.append(
            RepoTreeItem(
                path=item["path"],
                type=item["type"],
                sha=item["sha"],
                mode=item.get("mode"),
                size=item.get("size"),
                url=item.get("url")
            )
        )


    return RepoTreeResponse(tree=tree_items, truncated=tree_data.get("truncated"))



def index_repo(owner: str, repo: str, branch: str = "main"):
    """
    Indexes the repository by fetching all files and their contents.
    Returns a list of RepoIndexItem with path and content.

    Note: 1. To be used for repo indexing under 100 files if using the free token
          2. For larger repos, use the the clone method.
    """

    # 1. Fetch tree
    tree_response = fetch_repo_tree(owner, repo, branch)
    tree_items = tree_response.tree

    index_items = []

    for item in tree_items:

        # Skip directories 1
        if item.type != "blob":
            continue

        # Build contents API URL
        contents_url = (
            f"https://api.github.com/repos/{owner}/{repo}/contents/{item.path}"
            f"?ref={branch}"
        )

        # Fetch and decode file content
        try:
            file_data = fetch_file_content(contents_url)
        except Exception:
            continue

        index_items.append(
            RepoIndexItem(
                path=item.path,
                content=file_data.get("file_content", "")
            )
        )

    return RepoIndexResponse(items=index_items)



