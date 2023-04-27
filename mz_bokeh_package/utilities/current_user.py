import os
from bokeh.io import curdoc

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient


class CurrentUser:
    """
    Class with static methods for getting information about the current user
    """

    _users = {}

    @classmethod
    def get_user_info(cls, api_key: str | None) -> dict:
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

        api_key = api_key or CurrentUser.get_api_key()
        if api_key:
            user_info = MZGraphQLClient().get_user(api_key)
            if session_id:
                cls._cache_user_info(session_id, user_info)
            return user_info
        else:
            raise ValueError("an api_key is required in order to fetch the user info.")

    @classmethod
    def get_user_id(cls) -> str | None:
        """get the user_id of the current user

        Returns:
            the user_id of the current user
        """

        return cls.get_user_info(CurrentUser.get_api_key()).get("id")

    @classmethod
    def get_user_name(cls) -> str:
        """get the name of the current user, this is obtained by an API call

        Returns:
            the name of the current user
        """

        return cls.get_user_info(CurrentUser.get_api_key()).get("name")

    @staticmethod
    def get_api_key() -> str | None:
        """Get the api_key of the current user

        Returns:
            The api_key of the current user if it exists in either the environment variable or the request header,
            None otherwise.
        """
        # in the development environment, allow overriding the api_key and user_key via env variables
        if Environment.get_environment() == 'dev':
            api_key = os.getenv('API_KEY')
            return api_key

        # get the api_key from the request header
        api_keys = curdoc().session_context.request.arguments.get("api_key") if curdoc().session_context else None
        if api_keys is not None and len(api_keys) == 1:
            api_key = api_keys[0]
        else:
            api_key = None

        return api_key

    @classmethod
    def _cache_user_info(cls, session_id: str, user_info: dict):
        CurrentUser._users[session_id] = user_info
        curdoc().on_session_destroyed(lambda session_context: CurrentUser._users.pop(session_id, None))
