from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent


def root() -> Path:
    return ROOT_DIR

def conf(configuration: str) -> Path:
    return ROOT_DIR / "conf" / configuration
