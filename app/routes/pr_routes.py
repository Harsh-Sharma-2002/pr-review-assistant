from fastapi import APIRouter
from ..schema import *
from ..services.pr_services import fetch_pr_files, fetch_all_file_contents


router = APIRouter(tags=["pr services"])


##############################################################################################
##############################################################################################
##############################################################################################


@router.get("/fetch_pr_files_meta", response_model=PRFilesResponse)
def fetch_pr_files_route(owner: str, repo: str, pr_number: int):
    """
    API route to fetch list of changed files in a PR, including:
    - filename
    - status
    - patch (diff)
    - contents_url (for fetching full file content)
    """
    return fetch_pr_files(owner, repo, pr_number)


##############################################################################################
##############################################################################################
##############################################################################################


@router.get("/fetch_all_file_contents", response_model=AllFilesContentResponse)
def fetch_all_file_contents_route(owner: str, repo: str, pr_number: int):
    """
    API route to fetch full decoded contents for all changed files in a PR.
    Combines:
    - filename
    - patch
    - full decoded content (if available)
    """
    return fetch_all_file_contents(owner, repo, pr_number)




##############################################################################################
##############################################################################################
##############################################################################################



