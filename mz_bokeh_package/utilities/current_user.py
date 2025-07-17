import os
from bokeh.io import curdoc

from .environment import Environment
from .graphql_api import MZGraphQLClient
from .helpers import get_api_key_from_query_arguments, get_auth_token_from_query_arguments


class FetchUserInfoError(Exception):
    """ This exception is raised when an API key is not provided and the user info is not cached for a session. """
    pass


class CurrentUser:
    """
    Class with static methods for getting information about the current user
    """

    _users_cache = {}
    _auth_token_cache = {}

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
        api_key = get_api_key_from_query_arguments(query_arguments)

        return api_key

    @staticmethod
    def get_auth_token() -> str | None:
        """Get the auth token of the current user

        Returns:
            The auth token of the current user if it exists in the request header, otherwise None.
        """

        # in the development environment, allow overriding the api_key and user_key via env variables
        if Environment.get_environment() == 'dev':
            auth_token = os.getenv('AUTH_TOKEN')
            return auth_token

        session_id = CurrentUser._get_session_id()
        if session_id and session_id in CurrentUser._auth_token_cache:
            return CurrentUser._auth_token_cache[session_id]

        query_arguments = curdoc().session_context.request.arguments
        auth_token = get_auth_token_from_query_arguments(query_arguments)
        return auth_token
    
    @staticmethod
    def update_auth_token(new_auth_token: str) -> None:
        """Update the auth token for the current session"""
        session_id = CurrentUser._get_session_id()
        if session_id:
            CurrentUser._auth_token_cache[session_id] = new_auth_token

    @classmethod
    def _get_user_info(cls) -> dict:
        session_id = cls._get_session_id()
        if session_id and session_id in CurrentUser._users_cache:
            return CurrentUser._users_cache[session_id]

        api_key = CurrentUser.get_api_key()
        auth_token = CurrentUser.get_auth_token()
        if api_key or auth_token:
            user_info = MZGraphQLClient.get_user(api_key, auth_token)
            if session_id:
                cls._cache_user_info(session_id, user_info)
            return user_info
        else:
            raise FetchUserInfoError("an api_key or auth_token is required in order to fetch the user info.")

    @classmethod
    def _cache_user_info(cls, session_id: str, user_info: dict):
        CurrentUser._users_cache[session_id] = user_info
        curdoc().on_session_destroyed(cls._clear_session_cache)

    @classmethod
    def _clear_session_cache(cls, session_context):
        """Clear all cached data for a session when it's destroyed"""
        session_id = session_context.id
        CurrentUser._users_cache.pop(session_id, None)
        CurrentUser._auth_token_cache.pop(session_id, None)

    @staticmethod
    def _get_session_id() -> str | None:
        return curdoc().session_context.id if curdoc().session_context else None
