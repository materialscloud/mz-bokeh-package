import os
from os.path import abspath, dirname, isdir, join
from typing import Union


def get_temp_dir_path():
    """Returns The absolute path to the "temp" folder.
    """

    current_dir = dirname(__file__)
    return abspath(join(current_dir, "../temp"))


def get_api_key_from_query_arguments(query_arguments: dict) -> str | None:
    """Get API key from the provided query arguments.

    Args:
        query_arguments: A dictionary containing query arguments.

    Returns:
        The API key if found in the query arguments and only one is present, otherwise None.
    """

    api_keys = query_arguments.get("api_key")
    if api_keys is not None and len(api_keys) == 1:
        api_key = api_keys[0]
        if isinstance(api_key, bytes):
            api_key = api_key.decode('utf8')
        return api_key
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
