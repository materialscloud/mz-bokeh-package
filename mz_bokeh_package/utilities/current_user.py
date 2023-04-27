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

        session_id = curdoc().session_context.id if curdoc().session_context else None

        if session_id and session_id in CurrentUser._users:
            return CurrentUser._users[session_id]

        if session_id is None and api_key is None:
            raise ValueError("api_key or an active session required to fetch user info.")

        api_key = api_key or CurrentUser.get_api_key()

        if not api_key:
            raise ValueError("api_key or an active session required to fetch user info.")

        user_info = asdict(MZGraphQLClient().get_user(api_key))

        if session_id:
            CurrentUser._users[session_id] = user_info
            curdoc().on_session_destroyed(lambda: CurrentUser._users.pop(session_id, None))

        return user_info

    @staticmethod
    def get_user_id() -> str | None:
        """get the user_id of the current user

        Returns:
            the user_id of the current user
        """

        return MZGraphQLClient().get_user(CurrentUser.get_api_key()).id

    @staticmethod
    def get_user_name() -> str:
        """get the name of the current user, this is obtained by an API call

        Returns:
            the name of the current user
        """

        return MZGraphQLClient().get_user(CurrentUser.get_api_key()).name

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
