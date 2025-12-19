def chunnk_text(text: str, chunk_size: int = 8000, overlap: int = 200):
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append((chunk_id, chunk))
        chunk_id += 1
        
        start += chunk_size - overlap

    return chunks