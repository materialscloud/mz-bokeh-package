"""
This module takes care of the authentication of calls to bokeh apps

"""

import os
from bokeh.io import curdoc
from tornado.web import RequestHandler

from mz_bokeh_package import utilities


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

    return CurrentUser.get_user_id()


def get_login_url(request_handler: RequestHandler) -> str:
    """gets the login url for failed authentication depending on the environment

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return utilities.Environment.get_error_page_url()


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
        # in the development environment, allow overriding the api_key and user_key via env variables
        if utilities.Environment.get_environment() == 'dev':
            api_key = os.getenv('API_KEY')
            return api_key

        query_arguments = curdoc().session_context.request.arguments

        # get the api_key from the request header
        api_keys = query_arguments.get("api_key")
        if api_keys is not None and len(api_keys) == 1:
            api_key = api_keys[0]
        else:
            api_key = ""

        return api_key

    @staticmethod
    def get_user_id() -> str | None:
        """get the user_id of the current user

        Returns:
            the user_id of the current user
        """

        return utilities.MZGraphQLClient().get_user().id

    @staticmethod
    def get_user_name() -> str:
        """get the name of the current user, this is obtained by an API call

        Returns:
            the name of the current user
        """

        return utilities.MZGraphQLClient().get_user().name
