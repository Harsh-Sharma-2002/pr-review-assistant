import os
import requests
import base64

def fetch_file_content(contents_url: str):
    """
    Fetches full content of a file given its contents_url from GitHub API.
    Decodes base64 content to return plain text.
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }   

    response = requests.get(contents_url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed: {response.text}"}
    
    data = response.json()
    encoded_content = data.get("content")
    if not encoded_content:
        raise Exception("No content found in the response")
    
    decoded_bytes = base64.b64decode(encoded_content)
    decoded_content = decoded_bytes.decode("utf-8", errors="replace")

    return {
        "file_path": data.get("path"),
        "file_content": decoded_content
    }