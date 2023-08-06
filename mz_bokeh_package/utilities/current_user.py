import os
from bokeh.io import curdoc

from .environment import Environment
from .graphql_api import MZGraphQLClient
from .helpers import get_argument_from_query_arguments


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
        """Retrieves the user ID of the currently active viewer.

        Returns:
            the user ID of the currently active viewer.
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
        """Get the api_key of the current active viewer.

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
        api_key = get_argument_from_query_arguments(query_arguments, "api_key")

        return api_key

    @classmethod
    def get_token(cls) -> str:
        """ Retrieves the current active viewer authentication token.

        Returns:
            the token of the currently active viewer.
        """
        user_info = cls._get_user_info()
        return user_info["token"]

    @classmethod
    def update_token(cls, token: str):
        session_id = cls._get_session_id()
        if session_id and session_id in CurrentUser._users_cache:
            CurrentUser._users_cache[session_id]["token"] = token
        else:
            raise FetchUserInfoError("a session is required in order update the user token.")

    @classmethod
    def _get_user_info(cls) -> dict:
        session_id = cls._get_session_id()
        if session_id and session_id in CurrentUser._users_cache:
            return CurrentUser._users_cache[session_id]

        api_key = CurrentUser.get_api_key()
        token = CurrentUser._get_initial_token()
        if api_key or token:
            user_info = MZGraphQLClient.get_user(api_key, token)
            user_info["token"] = token
            if session_id:
                cls._cache_user_info(session_id, user_info)
            return user_info
        else:
            raise FetchUserInfoError("The user's credentials has not been provided.")

    @classmethod
    def _cache_user_info(cls, session_id: str, user_info: dict):
        CurrentUser._users_cache[session_id] = user_info
        curdoc().on_session_destroyed(lambda session_context: CurrentUser._users_cache.pop(session_context.id, None))

    @staticmethod
    def _get_session_id() -> str | None:
        return curdoc().session_context.id if curdoc().session_context else None

    @staticmethod
    def _get_initial_token() -> str | None:
        query_arguments = curdoc().session_context.request.arguments
        return get_argument_from_query_arguments(query_arguments, "auth_token")
