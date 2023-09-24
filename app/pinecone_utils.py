import os
from typing import List

import pinecone

PINECONE_APIKEY = os.environ["PINECONE_APIKEY"]


def get_index(index_name: str) -> pinecone.Index:
    """Get index in Pinecone vector database

    Args:
        index_name (str): Index name

    Returns:
        pinecone.Index
    """
    pinecone.init(api_key=PINECONE_APIKEY, environment="us-west1-gcp")
    index = pinecone.Index(index_name)
    return index


def search(index: str, input_emb: List[float], top_k: int) -> List[int]:
    """Search the IDs of top similar images

    Args:
        index (str): index name
        input_emb (List[float]): input embedding
        top_k (int): number of top similar images

    Returns:
        List[int]: The IDs of top similar images
    """
    matching = index.query(vector=input_emb, top_k=top_k, include_values=True)[
        "matches"
    ]
    match_ids = [match_id["id"] for match_id in matching]
    return match_ids
