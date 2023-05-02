"""
This module takes care of the authentication of calls to bokeh apps

"""
from tornado.web import RequestHandler

from .environment import Environment
from .graphql_api import GraphqlQueryError
from .current_user import CurrentUser


def get_user(request_handler: RequestHandler) -> bool | None:
    """
    authenticate user based on the api_key that is sent via the query parameters of the request and
    return the user_id if the user is authenticated and otherwise return None

    Args:
        request_handler: a tornado RequestHandler object that contains the query parameters of the request,
            which contains the api_key of the user

    Returns:
        True when authentication is successful, and otherwise None
    """

    # bypass authentication in the case of health.py dashboard to allow GCP to perform health checks
    if request_handler.request.path.split("/")[-1] in ("health", "error"):
        return True

    query_arguments = request_handler.request.query_arguments
    # accessing two private methods since get_user is conceptually part of CurrentUser
    api_key = CurrentUser._get_api_key_from_query_arguments(query_arguments)  # noqa F401
    try:
        CurrentUser._get_user_info(api_key)  # noqa F401
    except GraphqlQueryError:
        return None

    return True


def get_login_url(request_handler: RequestHandler) -> str:
    """gets the login url for failed authentication depending on the environment

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return Environment.get_webapp_host()
