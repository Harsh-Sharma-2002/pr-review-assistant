from fastapi import APIRouter
from ..schema import *
from ..services.repo_index_services import index_repo, fetch_repo_tree



router = APIRouter(tags=["repo_index"])

@router.get("/fetch_repo_tree",response_model=RepoTreeResponse)
def fetch_repo_tree_route(owner: str, repo: str, branch: str = "main"):
    """
    API route to fetch the repository tree for a given branch.
    """
    return fetch_repo_tree(owner, repo, branch)


##############################################################################################
##############################################################################################
##############################################################################################

@router.get("/index_repo_crawl",response_model=RepoIndexResponse)
def index_repo_crawl(owner: str, repo: str, branch: str = "main"):
    """
    Indexes the repository by fetching all files and their contents.
    Returns a list of RepoIndexItem with path and content.

    Note: 1. To be used for repo indexing under 100 files if using the free token
          2. For larger repos, use the the clone method.
    """
    return index_repo(owner, repo, branch)




##############################################################################################
##############################################################################################
##############################################################################################


# @router.get("/index_repo_clone",response_model=RepoIndexResponse) 
# def index_repo_clone(owner: str, repo: str, branch: str = "main"):
#     """
#     Indexes the repository by cloning it and reading files directly.
#     Returns a list of RepoIndexItem with path and content.

#     Note: Requires 'git' to be installed and accessible in the environment.
#     """
#     import tempfile
#     import subprocess
#     import shutil

#     # Create a temporary directory to clone the repo
#     temp_dir = tempfile.mkdtemp()

#     # try:
#     #     # Clone the repository
#     #     repo_url = f"