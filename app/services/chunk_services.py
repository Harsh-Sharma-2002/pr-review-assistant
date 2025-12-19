from ..schema import *


##################################################################################################################
##################################################################################################################

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200):
    """
    Clean and safe chunking:
    - Prevent infinite loops
    - Remove whitespace-only chunks
    - Normalize newlines
    """
    
    # Sanity check
    if overlap >= chunk_size:
        overlap = chunk_size // 4  # fallback safety

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(normalized):
        end = start + chunk_size
        chunk = normalized[start:end].strip()

        if chunk:  # skip empty or whitespace chunks
            chunks.append((chunk_id, chunk))

        chunk_id += 1
        start += chunk_size - overlap

    return chunks


##################################################################################################################
##################################################################################################################

def chunk_repo_contents(repo_index: RepoIndexResponse,chunk_size: int = 800,overlap: int = 200) -> RepoChunksResponse:
    
    repo_chunks = []
    global_chunk_id = 0

    for item in repo_index.items:

        file_path = item.path
        content = item.content

        # Skip empty files
        if not content.strip():
            continue

        # Skip extremely large files
        if len(content) > 200_000:
            continue

        chunks = chunk_text(content, chunk_size, overlap)

        for local_id, chunk_content in chunks:
            repo_chunks.append(
                RepoChunk(
                    file_path=file_path,
                    chunk_id=global_chunk_id,
                    content=chunk_content
                )
            )
            global_chunk_id += 1

    return RepoChunksResponse(chunks=repo_chunks)


##################################################################################################################
##################################################################################################################