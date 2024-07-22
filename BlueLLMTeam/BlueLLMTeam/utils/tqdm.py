import os
from tqdm import tqdm, trange
from dotenv import load_dotenv


load_dotenv()


def tqdm_wrapper(*args, **kwargs) -> tqdm:
    disable = kwargs.pop("disable", os.getenv("DISABLE_TQDM", "false").lower() == "true")
    return tqdm(*args, **kwargs, disable=disable)


def trange_wrapper(*args, **kwargs) -> tqdm:
    disable = kwargs.pop("disable", os.getenv("DISABLE_TQDM", "false").lower() == "true")
    return trange(*args, **kwargs, disable=disable)
