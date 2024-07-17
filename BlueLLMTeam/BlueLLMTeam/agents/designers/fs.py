import logging
from tqdm import tqdm
from pathlib import Path


logger = logging.getLogger(__name__)

def safe_generator(generator):
    while True:
        try:
            yield next(generator)
        except StopIteration:
            break
        except Exception as e:
            logger.warning(f'Failed to read contents: {e}')
            


def copy_local_filenames(src_dir, dest_dir, max_depth: int = 3):
    """
    Copy all filenames from src_dir to dest_dir without copying the file contents.

    Parameters:
    src_dir (str): The source directory.
    dest_dir (str): The destination directory.
    """
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)

    # Check if the source directory exists
    if not src_path.exists():
        raise ValueError(f"Source directory '{src_dir}' does not exist.")
    
    # Iterate over all files and directories in the source directory
    for item in tqdm(list(safe_generator(src_path.rglob('*'))), desc="Copying more pickle files", leave=False):
        try:
            # Create corresponding path in the destination directory
            relative_path = item.relative_to(src_path)
            dest_item = dest_path / relative_path

            depth = len(relative_path.parts)

            if depth > max_depth:
                continue
            
            if item.is_dir():
                # Create directory in the destination path
                dest_item.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                # Create an empty file in the destination path
                dest_item.parent.mkdir(parents=True, exist_ok=True)
                dest_item.touch(exist_ok=True)
        except PermissionError as e:
            logger.warning(f"Could not copy file/folder {e.filename} due to permission errors")
            pass
