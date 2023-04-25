import os
from dataclasses import asdict
from bokeh.io import curdoc

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient


class CurrentUser:
    """
    Class with static methods for getting information about the current user
    """

    _users = {}

    @staticmethod
    def get_user_info(api_key: str | None) -> dict:
        """Retrieves user information for the current session or API key, caching the information for future use.

        Args:
            api_key: unique user api key.

        Returns:
            dictionary of user "id" and "name".

        Raises:
             a ValueError if neither a session nor an API key is provided.
        """

        session_id = curdoc().session_context.id

        if session_id and session_id in CurrentUser._users:
            return CurrentUser._users[session_id]

        if not session_id and api_key is None:
            raise ValueError("api_key or an active session required to fetch user info.")

        api_key = api_key or CurrentUser.get_api_key()

        if not api_key:
            raise ValueError("api_key or an active session required to fetch user info.")

        user_info = asdict(MZGraphQLClient.get_user(api_key))
        CurrentUser._users[session_id] = user_info

        if session_id:
            curdoc().on_session_destroyed(lambda: CurrentUser._remove_user_info(session_id))

        return user_info

    @staticmethod
    def get_user_id() -> str | None:
        """get the user_id of the current user

        Returns:
            the user_id of the current user
        """

        # in the development environment, allow overriding the api_key via env variables
        if Environment.get_environment() == 'dev':
            user_id = os.getenv('USER_KEY')
        else:
            user_id = MZGraphQLClient().get_user().id

        return user_id

    @staticmethod
    def get_user_name() -> str:
        """get the name of the current user, this is obtained by an API call

        Returns:
            the name of the current user
        """

        return MZGraphQLClient().get_user().name

    @staticmethod
    def get_api_key() -> str:
        """get the api_key of the current user

        Returns:
            the api_key of the current user
        """
        # in the development environment, allow overriding the api_key and user_key via env variables
        if Environment.get_environment() == 'dev':
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
    def _remove_user_info(session_id):
        del CurrentUser._users[session_id]
