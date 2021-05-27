"""This file includes convenience functions.
"""

import os
import json
import requests
from os.path import dirname, join, abspath, isdir, basename
from functools import partial
from typing import Dict, Optional, Union

from mz_bokeh_package.auth import CurrentUser
from mz_bokeh_package.environment import get_request_url
from mz_bokeh_package.custom_widgets.select import CustomSelect, CustomMultiSelect


def _get_temp_dir_path():
    """Returns The absolute path to the "temp" folder.
    """

    current_dir = dirname(__file__)
    return abspath(join(current_dir, "../temp"))


def _save_file(file_name: str, file_content: Union[str, bytes]) -> str:
    """Saves a file to the "temp" folder.

    Args:
        file_name (str): Name of the file (including format).
        file_content (Union[str, bytes]): Content of the file.

    Returns:
        str: Absolute path to the file.
    """

    temp_path = _get_temp_dir_path()

    if not isdir(temp_path):
        os.mkdir(temp_path)

    file_path = join(temp_path, file_name)

    write_mode = "wb+" if isinstance(file_content, bytes) else "w+"
    with open(file_path, write_mode) as f:
        f.write(file_content)

    return file_path


def _clean_temp_folder():
    temp_path = _get_temp_dir_path()
    for filename in os.listdir(temp_path):
        os.remove(join(temp_path, filename))


def _download_image(url: str) -> bytes:
    """Downloads an image from a given url path.

    Args:
        url (str): URL address of the image.

    Returns:
        bytes: Image data.
    """
    res = requests.get(url)

    return res._content


class Bokeh:

    @staticmethod
    def async_event_handler(func):
        """This function can be used as a decorator for callbacks in order to display a loading banner
        while the callback is running.
        """

        def outer(self, attr, old, new):
            self._state["is_loading"] = True
            self._doc.add_next_tick_callback(partial(inner, func, self, attr, old, new))

        def inner(f, self, attr, old, new):
            f(self, attr, old, new)
            self._state["is_loading"] = False

        return outer

    @staticmethod
    def silent_property_change(object_name, property, value, event_handler):
        """This function allows updating any of the properties in event_handlers without triggering the event handler.
        """
        object_dict = event_handler[object_name]
        object_dict['object'].remove_on_change(property, object_dict['properties'][property])
        object_dict['object'].update_from_json({property: value})
        object_dict['object'].on_change(property, object_dict['properties'][property])

    @staticmethod
    def create_custom_multi_select(title: str) -> CustomMultiSelect:
        """This function creates a custom multi select filter with the title given.
        """
        return CustomMultiSelect(
            include_select_all=True,
            enable_filtering=True,
            options=[],
            value=[],
            title=title,
            sizing_mode='scale_width',
            margin=[10, 10, 10, 5],
            css_classes=['custom_select', 'custom']
        )

    @staticmethod
    def create_custom_select(title: str) -> CustomSelect:
        """This function creates a custom single select filter with the title given.
        """
        return CustomSelect(
            options=[],
            value="",
            title=title,
            enable_filtering=True,
            margin=[10, 10, 10, 5],
            allow_non_selected=True,
            sizing_mode='scale_width',
            css_classes=['custom_select', 'custom'])


class ExternalApi:

    @staticmethod
    def upload(metadata: dict, data_files: Optional[list] = None):
        """Uploads MZ components using MZ external API.

        Args:
            metadata (dict): MZ Metadata object.
            data_files (Optional[List[Tuple[str, bytes]]], optional): A list of data files to upload.
                each file should be represented by a tuple that includes the file name and
                its content i.e (filename, content). Defaults to None.
        """

        # convert metadata object to string
        meta_file_content = json.dumps(metadata, indent=2)

        # save files in hard disk
        files_paths = [
            _save_file(name, content)
            for name, content in [("meta.json", meta_file_content), *data_files]
        ]

        # user credentials
        params = {
            "key": CurrentUser.get_api_key(),
            "uid": CurrentUser.get_user_key()
        }

        # construct a list of files to upload via a POST HTTP request
        files = [
            ("data" if basename(path) == 'meta.json' else 'files', open(path, "rb"))
            for path in files_paths
        ]

        # upload the files. a response object will be returned with a success or fail message.
        requests.post(get_request_url("upload/items"), files=files, params=params)

        # remove files
        _clean_temp_folder()

    @staticmethod
    def parse_file(file_content: Union[str, bytes], processing_parameters_code: str) -> Dict[str, Union[str, dict]]:
        """parse a bokeh FileInput widget with a given processing parameters code.

        Args:
            file_content (Union[str, bytes]): Content of the file to parse.
            processing_parameters_code (str): Processing parameters code e.g. #PE-ED-F-ED.

        Raises:
            Exception: Whenever the parsing process has failed.

        Returns:
            Dict[str, Union[str, dict]]: a dictionary that contains:
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

        # get parser endpoint
        parser_route = "parse/{}".format(processing_parameters_code.lstrip("#"))
        url = get_request_url(parser_route)

        # send request to API
        res = requests.post(
            url=url,
            files=[('files', file_content)],
            params=params
        ).json()

        # parsing process has failed
        if res.get('error'):
            raise Exception(f"Failed to parse file: {res.get('error')}")

        # parsed data is an image
        if res['data_type'] == 'image':
            processed_data = _download_image(res['data'])

        # parsed data is either a JSON or text
        else:
            processed_data = res['data']

        return {
            'data_type': res['data_type'],
            'data': processed_data
        }
