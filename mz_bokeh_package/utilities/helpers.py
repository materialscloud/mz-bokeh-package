import os
from os.path import abspath, dirname, isdir, join
from typing import Union
import requests


def get_temp_dir_path():
    """Returns The absolute path to the "temp" folder.
    """

    current_dir = dirname(__file__)
    return abspath(join(current_dir, "../temp"))


def save_file(file_name: str, file_content: Union[str, bytes]) -> str:
    """Saves a file to the "temp" folder.

    Args:
        file_name: Name of the file (including format).
        file_content: Content of the file.

    Returns:
        Absolute path to the file.
    """

    temp_path = get_temp_dir_path()

    if not isdir(temp_path):
        os.mkdir(temp_path)

    file_path = join(temp_path, file_name)

    write_mode = "wb+" if isinstance(file_content, bytes) else "w+"
    with open(file_path, write_mode) as f:
        f.write(file_content)

    return file_path


def clean_temp_folder():
    temp_path = get_temp_dir_path()
    for filename in os.listdir(temp_path):
        os.remove(join(temp_path, filename))


def download_image(url: str) -> bytes:
    """Downloads an image from a given url path.

    Args:
        url: URL address of the image.

    Returns:
        Image data.
    """
    res = requests.get(url)

    return res._content
