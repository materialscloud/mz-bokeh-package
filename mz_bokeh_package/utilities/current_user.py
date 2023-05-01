import os
from bokeh.io import curdoc

from mz_bokeh_package.utilities.environment import Environment
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient


class FetchUserInfoError(Exception):
    """ This exception is raised when an API key is not provided and the user info is not cached for a session. """
    pass


class CurrentUser:
    """
    Class with static methods for getting information about the current user
    """

    _users_cache = {}

    @classmethod
    def get_user_id(cls) -> str:
        """Retrieves the user ID of the currently active viewer

        Returns:
            the user ID of the currently active viewer
        """
        user_info = cls._get_user_info()
        return user_info["id"]

    @classmethod
    def get_user_name(cls) -> str:
        """Retrieves the name of the currently active viewer.

        Returns:
            the name of the currently active viewer.
        """
        user_info = cls._get_user_info()
        return user_info["name"]

    @staticmethod
    def get_api_key() -> str | None:
        """Get the api_key of the current user

        Returns:
            The api_key of the current user if it exists in either the environment variable or the request header,
            otherwise None.
        """

        # in the development environment, allow overriding the api_key and user_key via env variables
        if Environment.get_environment() == 'dev':
            api_key = os.getenv('API_KEY')
            return api_key

        # get the api_key from the request header
        query_arguments = curdoc().session_context.request.arguments
        api_key = CurrentUser._get_api_key_from_query_arguments(query_arguments)

        return api_key

    @staticmethod
    def _get_api_key_from_query_arguments(query_arguments: list) -> str | None:
        api_keys = query_arguments.get("api_key")
        if api_keys is not None and len(api_keys) == 1:
            api_key = api_keys[0]
            if isinstance(api_key, bytes):
                api_key = api_key.decode('utf8')
            return api_key
        else:
            return None

    @classmethod
    def _get_user_info(cls, api_key: str | None) -> dict:
        session_id = cls._get_session_id()
        if session_id and session_id in CurrentUser._users_cache:
            return CurrentUser._users_cache[session_id]

        api_key = api_key or CurrentUser.get_api_key()
        if api_key:
            user_info = MZGraphQLClient.get_user(api_key)
            if session_id:
                cls._cache_user_info(session_id, user_info)
            return user_info
        else:
            raise FetchUserInfoError("an api_key is required in order to fetch the user info.")

    @classmethod
    def _cache_user_info(cls, session_id: str, user_info: dict):
        CurrentUser._users_cache[session_id] = user_info
        curdoc().on_session_destroyed(lambda session_context: CurrentUser._users_cache.pop(session_context.id, None))

    @staticmethod
    def _get_session_id() -> str | None:
        return curdoc().session_context.id if curdoc().session_context else None
