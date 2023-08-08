"""
This module is used for authentication with the Materials Zone platform when running a Bokeh server using the `bokeh
serve` command. The module contains two methods: get_user and get_login_url as specified in the Bokeh documentation:
    https://docs.bokeh.org/en/2.4.3/docs/user_guide/server.html#auth-module
The get_user method is responsible for authenticating the user and the get_login_url returns the url the user should
be forwarded to when authentication fails.

To enable authentication, pass the absolute path of this module via the `--auth-module` flag to the `bokeh serve`
command as follows:

   bokeh serve <relative path of dashboard> --auth-module=<absolute to auth.py>

To authenticate when running a dashboard, provide the User API Key in the URL arguments as follows:
   http://localhost:5006/histogram?api_key=<api key>
"""
from tornado.web import RequestHandler

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient, GraphqlQueryError
from mz_bokeh_package.utilities.helpers import get_argument_from_query_arguments


def get_user(request_handler: RequestHandler) -> bool | None:
    """Function used by the Bokeh server for user authentication. The function authenticates the user by fetching the
    user's API key from the URL query arguments and sending a query to the GraphQL API. When authentication is
    successful, True is returned, when it fails, None is returned. See the module docstring for more details.

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
    api_key = get_argument_from_query_arguments(query_arguments, "api_key")
    token = get_argument_from_query_arguments(query_arguments, "auth_token")
    try:
        MZGraphQLClient.get_user(api_key, token)
    except GraphqlQueryError:
        return None

    return True


def get_login_url(request_handler: RequestHandler) -> str:
    """Function used by the Bokeh server to get the url the user should be forwarded to when authentication fails.
    See the module docstring for more details.

    Returns:
        the MZ App URL (environment dependant) to redirect to if authentication fails
    """

    return Environment.get_webapp_host()
