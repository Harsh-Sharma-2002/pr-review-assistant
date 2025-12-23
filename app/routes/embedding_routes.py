from fastapi import APIRouter, HTTPException
from ..services.embedding_services import embed_text
from ..schema import (
    EmbedRequest,
    EmbedResponse,
    BatchEmbedRequest,
    BatchEmbedResponse
)

router = APIRouter(tags=["embedding"])


# #############################################################################################################################
@router.post("/single", response_model=EmbedResponse)
def embed_single_route(req: EmbedRequest):
    """
    Embed a single text string using an explicitly specified provider.
    """

    if not req.provider:
        raise HTTPException(
            status_code=400,
            detail="Embedding provider must be explicitly specified."
        )

    try:
        result = embed_text(req.text, provider=req.provider)
        return EmbedResponse(
            embedding=result["embedding"],
            provider=result["provider"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# #############################################################################################################################
@router.post("/batch", response_model=BatchEmbedResponse)
def embed_batch(req: BatchEmbedRequest):
    """
    Embed a list of texts using an explicitly specified provider.
    Provider selection applies to all texts.
    """

    if not req.provider:
        raise HTTPException(
            status_code=400,
            detail="Embedding provider must be explicitly specified."
        )

    embeddings = []

    try:
        for text in req.texts:
            result = embed_text(text, provider=req.provider)
            embeddings.append(
                EmbedResponse(
                    embedding=result["embedding"],
                    provider=result["provider"]
                )
            )

        return BatchEmbedResponse(embeddings=embeddings)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# #############################################################################################################################
