import os
from bokeh.io import curdoc

from mz_bokeh_package.utilities.environment import Environment


class CurrentUser:
    """
    A singleton class with methods for getting information about the current user
    """
    _instances = {}

    @classmethod
    def __call__(cls):
        session_id = curdoc().session_context.id
        if session_id not in cls._instances:
            raise KeyError("Instance of CurrentUser has not been initiated in this session")
        return cls._instances[session_id]

    def __init__(self, user_id: str, user_name: str):
        self._user_id = user_id
        self._user_name = user_name

    @classmethod
    def add_instance(cls, user_id: str, user_name: str):
        session_id = curdoc().session_context.id
        if session_id in cls._instances:
            raise KeyError("Instance of CurrentUser already added in this session")
        cls._instances[session_id] = cls(user_id, user_name)

    def get_user_id(self) -> str | None:
        """get the user_id of the current user

        Returns:
            the user_id of the current user
        """

        return self._user_id

    def get_user_name(self) -> str:
        """get the name of the current user, this is obtained by an API call

        Returns:
            the name of the current user
        """

        return self._user_name

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
