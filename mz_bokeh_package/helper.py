import json
from os.path import abspath, dirname, join
import requests
import os
import base64
from typing import Union
from functools import partial
from typing import Optional

from .auth import CurrentUser
from .environment import get_request_url


def get_absolute_path(relative_path):
    current_dir = dirname(__file__)
    return abspath(join(current_dir, relative_path))


def get_temp_dir_path():
    return get_absolute_path('../temp')


def str_to_bytes(value):
    return base64.b64decode(value)


def decode_if_bytes(cls, data):
    try:
        data = data.decode()
    except (UnicodeDecodeError, AttributeError):
        pass
    return data


def clean_temp_folder():
    temp_path = get_temp_dir_path()
    for filename in os.listdir(temp_path):
        os.remove(join(temp_path, filename))


def open_file(file_name):
    temp_path = get_temp_dir_path()

    return partial(open, join(temp_path, file_name), 'rb')


def save(file_content: Union[dict, str], file_name:str):

    # save into temp folder
    temp_path = get_temp_dir_path()

    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)

    path = join(temp_path, file_name)

    if isinstance(file_content, dict):
        with open(path, 'w+') as f:
            json.dump(file_content, f, indent=2)
    else:
        with open(path, 'wb+') as f:
            f.write(str_to_bytes(file_content))

    return path


def download_image(url: str) -> bytes:
    """download an image that is located from a given url path.

    Args:
        url (str): path to the image file

    Returns:
        bytes: image data.
    """
    res = requests.get(url)

    return res._content


def parse_file(file_content: str, processing_parameters_code: str) -> dict:
    """parse a bokeh FileInput widget with a given processing parameters code.

    Args:
        file_content: the contents of the file to parse
        processing_parameters_code: processing parameters code e.g. #PE-ED-F-ED.

    Returns:
        dict[str, Union[str, dict]]: a dictionary that contains:
            data_type (str): the type of the processed file ('image' | 'json' | 'text').
            data (Union[str,dict]): this field's value depends on the data type:
                'image': download url for the processed image.
                'json': processed file data as a json object.
                'text': processed file data as a string.
    """

    # user credentials
    params = {
        "key": CurrentUser.get_api_key(),
        "uid": CurrentUser.get_user_key()
    }

    # file data
    data = str_to_bytes(file_content)

    # get parser endpoint
    parser_route =  "parse/{}".format(processing_parameters_code.lstrip("#"))
    url = get_request_url(parser_route)

    # send request to API
    res = requests.post(
        url=url,
        files=[('files', data)],
        params=params
    ).json()

    # parsing process has failed
    if res.get('error'):
        raise Exception(f"Failed to parse file: {res.get('error')}")

    # parsed data is an image
    if res['data_type'] == 'image':
        processed_data = download_image(res['data'])
    else:
        processed_data = res['data']

    return {
        'data_type': res['data_type'],
        'data': processed_data
    }


def upload(meta: dict, file_name_list: Optional[list] = None, file_list: Optional[list] = None):

    files = {
        'meta':
            {
                'path': 'meta.json',
                'content': meta
            }
    }

    if not len(file_list) == len(file_name_list):
        raise Exception("file_name_list and file_list should have the same length")

    for i, file_name in enumerate(file_name_list):
        files.update(
            {
                file_name: {
                    'path': file_name,
                    'content': file_list[i]
                }
            }
        )

    # save as files in hard disk
    for v in files.values():
        save(v['content'], v['path'])

    # user credentials
    params = {
        "key": CurrentUser.get_api_key(),
        "uid": CurrentUser.get_user_key()
    }

    # construct a list with the JSON file and the measurement data files
    files = [
        ('data' if k == 'meta' else 'files', open_file(v['path'])())
        for k, v in files.items()
    ]

    # run the post function to upload the file, a response object will be returned with a success or fail message
    res = requests.post(get_request_url("upload/items"), files=files, params=params)

    print(res.text)

    # remove files
    clean_temp_folder()

