"""
This module is used for authentication with the Materials Zone platform when running a Bokeh server using the `bokeh
serve` command.

To enable authentication, pass the absolute path of this module via the `--auth-module` flag to the `bokeh serve`
command as follows:

   bokeh serve <relative path of dashboard> --auth-module=<absolute to auth.py>

To authenticate when running a dashboard, provide the User API Key in the URL arguments as follows:
   http://localhost:5006/histogram?api_key=<api key>
"""
from tornado.web import RequestHandler

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient, GraphqlQueryError
from mz_bokeh_package.utilities.helpers import get_api_key_from_query_arguments


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
    if request_handler.request.path.endswith("/health"):
        return True

    query_arguments = request_handler.request.query_arguments
    api_key = get_api_key_from_query_arguments(query_arguments)
    try:
        MZGraphQLClient.get_user(api_key)
    except GraphqlQueryError:
        return None

    return True


def get_login_url(request_handler: RequestHandler) -> str:
    """gets the login url for failed authentication depending on the environment

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return Environment.get_webapp_host()
