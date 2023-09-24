import torch


class AppConfig:
    INPUT_RESOLUTION = 224
    INDEX_NAME = "fashion"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    DATA_PATH = "./data.csv"
    TOP_IMAGES = 8
    PORT_EXPOSE = 30000
