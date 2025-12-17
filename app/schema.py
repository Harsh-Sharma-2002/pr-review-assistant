from typing import List, Optional
from pydantic import BaseModel


# -----------------------------
# Model for ONE changed file (metadata only)
# -----------------------------
class FileChange(BaseModel):
    filename: str
    status: str
    patch: Optional[str] = None
    contents_url: Optional[str] = None


# -----------------------------
# Response for /fetch_pr_files
# -----------------------------
class PRFilesResponse(BaseModel):
    files: List[FileChange]


# -----------------------------
# Model for a single file's decoded content
# -----------------------------
class FileContent(BaseModel):
    filename: str
    content: Optional[str]  # may be None for binary files


# -----------------------------
# Model for a file with diff + content
# Used in /fetch_all_file_contents
# -----------------------------
class ExpandedFile(BaseModel):
    filename: str
    patch: Optional[str] = None
    content: Optional[str] = None


# Response for /fetch_all_file_contents
# -----------------------------
class AllFilesContentResponse(BaseModel):
    files: List[ExpandedFile]
