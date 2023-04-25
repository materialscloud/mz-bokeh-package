"""
This module takes care of the authentication of calls to bokeh apps

"""

from tornado.web import RequestHandler

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import GraphqlQueryError
from mz_bokeh_package.utilities.current_user import CurrentUser


def get_user(request_handler: RequestHandler) -> bool | None:
    """
    authenticate user based on api_key that are sent via the query parameters of the request and
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

    try:
        _ = CurrentUser.get_user_info(request_handler.request.query_arguments)
    except GraphqlQueryError:
        return None

    return True


def get_login_url(request_handler: RequestHandler) -> str:
    """gets the login url for failed authentication depending on the environment

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return Environment.get_webapp_host()
