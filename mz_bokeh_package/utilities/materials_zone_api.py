import json
import requests
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Union, Any

from .current_user import CurrentUser
from .helpers import download_image
from .environment import Environment


class MaterialsZoneApi:

    @staticmethod
    def upload(
        metadata: Dict[str, Any],
        data_files: Optional[List[Tuple[str, bytes]]] = None,
        user_api_key: Optional[str] = None
    ):
        """Uploads MZ components using MZ external API.

        Args:
            metadata (Dict[str, Any]): MZ Metadata object.
            data_files (Optional[List[Tuple[str, bytes]]]): A list of data files to upload.
                each file should be represented by a tuple that includes the file name and
                its content i.e (filename, content). Defaults to None.
            user_api_key (Optional[str]): The API key of the user who makes the request.
                Note, this parameter should be provided when using this function in a multi-threading manner.
                If not provided, an attempt is made to extract the API key from the Bokeh app's
                URL parameters (see CurrentUser.get_api_key() method). This attempt will fail when trying
                to run this function in a multi-threading manner since the app's session context misses the request
                info in such cases. Defaults to None.
        """

        # Convert metadata object to a file-like object.
        meta_file_content = json.dumps(metadata, indent=2).encode("utf-8")
        meta_file = BytesIO(meta_file_content)

        # Convert the data files to file-like objects.
        files = [("data", meta_file)]
        for (name, content) in data_files:
            data_file = BytesIO(content)
            data_file.name = name
            files.append(("files", data_file))

        # User credentials.
        params = {"api_key": user_api_key or CurrentUser.get_api_key()}

        # Upload the files.
        # A response object will be returned with a success or fail message.
        res = requests.post(Environment.get_request_url("items"), files=files, params=params)

        if res.status_code != 200:
            raise Exception(res.json()["error"])

        # Return API response
        return res

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
        params = {"api_key": CurrentUser.get_api_key()}

        # get parser endpoint
        parser_route = "parse/{}".format(processing_parameters_code.lstrip("#"))
        url = Environment.get_request_url(parser_route)

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
