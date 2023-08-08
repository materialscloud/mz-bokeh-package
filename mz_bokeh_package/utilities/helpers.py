import os
from os.path import abspath, dirname, isdir, join
from typing import Union
import requests


def get_temp_dir_path():
    """Returns The absolute path to the "temp" folder.
    """

    current_dir = dirname(__file__)
    return abspath(join(current_dir, "../temp"))


def get_argument_from_query_arguments(query_arguments: dict, argument: str) -> str | None:
    """Get a given argument from the provided query arguments.

    Args:
        query_arguments: A dictionary containing query arguments.
        argument: An argument name.

    Returns:
        The argument value if found in the query arguments and only one is present, otherwise None.
    """

    values = query_arguments.get(argument)
    if values is not None and len(values) == 1:
        value = values[0]
        if isinstance(value, bytes):
            value = value.decode('utf8')
        return value
    else:
        return None


def save_file(file_name: str, file_content: Union[str, bytes]) -> str:
    """Saves a file to the "temp" folder.

    Args:
        file_name (str): Name of the file (including format).
        file_content (Union[str, bytes]): Content of the file.

    Returns:
        str: Absolute path to the file.
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
        url (str): URL address of the image.

    Returns:
        bytes: Image data.
    """
    res = requests.get(url)

    return res._content
