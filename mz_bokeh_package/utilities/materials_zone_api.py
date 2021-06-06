import json
from os.path import basename
from typing import Dict, Optional, Union
import requests

from .auth import CurrentUser
from .environment import get_request_url
from .helpers import save_file, clean_temp_folder, download_image


class MaterialsZoneApi:

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
            save_file(name, content)
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
        clean_temp_folder()

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
            processed_data = download_image(res['data'])

        # parsed data is either a JSON or text
        else:
            processed_data = res['data']

        return {
            'data_type': res['data_type'],
            'data': processed_data
        }
