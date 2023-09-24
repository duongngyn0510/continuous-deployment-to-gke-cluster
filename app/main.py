import os
from io import BytesIO

import gdown
import imagehash
import torch
from config import AppConfig
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from loguru import logger
from PIL import Image
from pinecone_utils import get_index, search
from utils import *

INDEX_NAME = AppConfig.INDEX_NAME
index = get_index(INDEX_NAME)
logger.info(f"Connect to index {INDEX_NAME} in Pinecone successfully!")

DEVICE = AppConfig.DEVICE

if os.path.isfile("pretrained_clip.pt"):
    logger.info("Pretrained model already exists!")
else:
    file_id = "1dmqfp-yb8EhzwSjI9pZi6ZAeKjngdtaT"
    pretrained_file = "pretrained_clip.pt"
    gdown.download(
        f"https://drive.google.com/uc?id={file_id}", pretrained_file, quiet=False
    )
    logger.info("Download pretrained model successfully!")

model = torch.load("pretrained_clip.pt", map_location=torch.device(DEVICE))
model.eval()

if DEVICE == "cpu":
    for p in model.parameters():
        p.data = p.data.float()

logger.info("Load pretrained model successfully!")

app = FastAPI()
image_cache = {}
text_cache = {}


@app.post("/image_url")
async def image_url(image_file: UploadFile = File(...)):
    """Get image url with image file query

    Args:
        image_file (UploadFile)

    Returns:
        (List): List of top images url
    """
    request_image_content = await image_file.read()
    pil_image = Image.open(BytesIO(request_image_content))
    pil_hash = imagehash.average_hash(pil_image)
    logger.info(pil_hash)

    if pil_hash not in image_cache:
        logger.info("Getting related products!")
        image_embedding = get_image_embedding(model, DEVICE, pil_image)
        match_ids = search(index, image_embedding, top_k=AppConfig.TOP_IMAGES)
        image_cache[pil_hash] = match_ids
    else:
        logger.info("Getting related products from cache!")
        match_ids = image_cache[pil_hash]

    images_url = get_image_url(
        match_ids,
    )
    return images_url


@app.post("/display_image")
async def display_image(image_file: UploadFile = File(...)):
    """Display images from their urls with image file query

    Args:
        image_file (UploadFile)

    Returns:
        HTMLResponse
    """
    images_url = await image_url(image_file)
    html_content = display_html(images_url)
    return HTMLResponse(content=html_content)


@app.post("/text_url")
async def text_url(text_query: str):
    """Get image url with text query

    Args:
        text_query (str)

    Returns:
       (List): List of top images url
    """
    print
    if text_query not in text_cache:
        logger.info("Getting related products!")
        text_embedding = get_text_embedding(model, DEVICE, text_query)
        match_ids = search(index, text_embedding, top_k=AppConfig.TOP_IMAGES)
        text_cache[text_query] = match_ids
    else:
        logger.info("Getting related products from cache!")
        match_ids = text_cache[text_query]

    images_url = get_image_url(match_ids)
    return images_url


@app.post("/display_text")
async def display_text(text_query: str):
    """Display images from their urls with text query

    Args:
        text_query (str)

    Returns:
        HTMLResponse
    """
    images_url = await text_url(text_query)
    html_content = display_html(images_url)
    return HTMLResponse(content=html_content)
