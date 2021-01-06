"""
This module takes care of the authentication of calls to bokeh apps

"""

import requests
import os
from bokeh.io import curdoc
from tornado.web import RequestHandler
from typing import Optional

from .helper import decode_if_bytes
from .environment import get_request_url, get_error_page_url, get_environment


def get_user(request_handler: RequestHandler) -> str:
    """
    authenticate user based on api_key and user_key that are sent via the query parameters of the request and
    return the user_id if the user is authenticated and otherwise return None

    Args:
        request_handler: a tornado RequestHandler object that contains the query parameters of the request,
            which contains the api_key and user_key of the user

    Returns:
        the user id when authentication is successful, and otherwise None
    """

    # bypass authentication in the case of health.py dashboard to allow GCP to perform health checks
    if request_handler.request.path.split("/")[-1] in ("health", "error"):
        return "ok"

    query_arguments = request_handler.request.query_arguments

    # get the api_key from the request header
    api_keys = query_arguments.get("api_key")
    if not api_keys is None and len(api_keys) == 1:
        api_key = api_keys[0]
    else:
        api_key = ""

    # get the user_key from the request header
    user_keys = query_arguments.get("user_key")
    if not user_keys is None and len(user_keys) == 1:
        user_key = user_keys[0]
    else:
        user_key = ""

    # in the development environment, allow overriding the api_key and user_key via env variables
    if get_environment() == 'dev':
        api_key = os.getenv('API_KEY', api_key)
        user_key = os.getenv('USER_KEY', user_key)

    # authenticate the user using the MaterialsZone API by requesting the user_id
    user_id = get_user_from_api_key(api_key, user_key)

    return user_id


def get_login_url(request_handler: RequestHandler) -> str:
    """gets the login url for failed authentication depending on the environment

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return get_error_page_url()


def get_user_from_api_key(api_key: str, user_key: str) -> Optional[str]:
    """get the user_id using an API call by using the api_key and user_key

    Args:
        api_key: the api_key of the user
        user_key: the user fbkey of the user

    Returns:
        the user_id corresponding to the api_key and user_key or None if the two keys are invalid
    """

    # Add credentials to request parameters object
    params = {
        "key": api_key,
        "uid": user_key
    }

    # send a get request to get the user_id corresponding to the credentials
    response = requests.get(get_request_url("users/currentuser"), params=params)

    # extract the user ID from the response
    response_body = response.json()
    if 'user_id' in response_body:
        return response_body['user_id']
    else:
        return None


class CurrentUser:
    """
    Class with static methods for getting information about the current user
    """

    @staticmethod
    def get_api_key() -> str:
        """get the api_key of the current user

        Returns:
            the api_key of the current user
        """

        query_arguments = curdoc().session_context.request.arguments

        # get the api_key from the request header
        api_keys = query_arguments.get("api_key")
        if not api_keys is None and len(api_keys) == 1:
            api_key = api_keys[0]
        else:
            api_key = ""

        # in the development environment, allow overriding the api_key and user_key via env variables
        if get_environment() == 'dev':
            api_key = os.getenv('API_KEY', api_key)

        return api_key

    @staticmethod
    def get_user_key() -> str:
        """get the user_key of the current user

        Returns:
            the user_key of the current user
        """

        query_arguments = curdoc().session_context.request.arguments

        # get the api_key from the request header
        user_keys = query_arguments.get("user_key")
        if not user_keys is None and len(user_keys) == 1:
            user_key = user_keys[0]
        else:
            user_key = ""

        # in the development environment, allow overriding the api_key and user_key via env variables
        if get_environment() == 'dev':
            user_key = os.getenv('USER_KEY', user_key)

        # convert bytes to str (this comes to fix a problem that the user_key may come as type bytes from the header)
        user_key = decode_if_bytes(user_key)

        return user_key

    @staticmethod
    def get_user_id() -> str:
        """get the user_id of the current user, this is obtained by an API call

        Returns:
            the user_id of the current user
        """

        return get_user_from_api_key(CurrentUser.get_api_key(), CurrentUser.get_user_key())


