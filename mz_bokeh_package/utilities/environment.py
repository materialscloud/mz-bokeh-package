"""This module contains functions for obtaining environment (e.g. dev/staging/production) specific data
"""

import os


class Environment:

    @staticmethod
    def get_environment() -> str:
        """Get the current environment.

        Returns:
            str: the current environment, possible values are: 'dev', 'staging' or 'production'

        Raises:
            ValueError: Whenever the environment is invalid.
        """

        # in the kubernetes deployed containers, the environemnt variable ENVIRONMENT is set to staging/production
        env = os.getenv('ENVIRONMENT', 'dev')

        if env not in {"staging", "production", "dev"}:
            raise ValueError(f'The "{env}" environment is invalid. Valid environments: "staging"/"production"/"dev"')

        return env

    @classmethod
    def get_request_url(cls, endpoint: str) -> str:
        """Converts an endpoint of an API request to a request url. The host should be set in the environment variable
        'API_HOST'.

        Args:
            endpoint: the endpoint of the request

        Returns:
            the full URL of the request

        Raises:
            ValueError: When the environment variable `API_HOST` is not set.
        """
        host = Environment._get_host_from_env_var('API_HOST')
        return f"{host}/{endpoint}"

    @classmethod
    def get_graphql_api_url(cls) -> str:
        """Returns the url of the GraphQL API Server. The host should be set in the environment variable
        'GRAPHQL_API_HOST'.

        Returns:
            the full URL of the GraphQL API server

        Raises:
            ValueError: When the environment variable `GRAPHQL_API_HOST` is not set.
        """
        host = Environment._get_host_from_env_var('GRAPHQL_API_HOST')
        return f"{host}"

    @classmethod
    def get_parser_service_url(cls, endpoint: str) -> str:
        """Converts an endpoint of the Parser Service to a request url. The host should be set in the environment
        variable 'PARSER_SERVICE_HOST'.

        Args:
            endpoint: the endpoint of the request

        Returns:
            the full URL of the request

        Raises:
            ValueError: When the environment variable `PARSER_SERVICE_HOST` is not set.
        """

        host = Environment._get_host_from_env_var('PARSER_SERVICE_HOST')
        return f"{host}/{endpoint}"

    @classmethod
    def get_webapp_host(cls) -> str:
        """Get the web app host as set in the environment variable WEBAPP_HOST.

        Returns:
            str: Web app host.

        Raises:
            ValueError: When the environment variable `WEBAPP_HOST` is not set.
        """
        return Environment._get_host_from_env_var('WEBAPP_HOST')

    @classmethod
    def _get_host_from_env_var(cls, env_var_name: str):
        host = os.getenv(env_var_name)
        if not host:
            raise ValueError(f'The {env_var_name} environment variable is not set.')
        return host

    @classmethod
    def get_error_page_url(cls) -> str:
        """get the url for the MaterialsZone app

        Returns:
            the URL of the MaterialsZone app
        """

        env = cls.get_environment()

        if env in {'staging', 'dev'}:
            return "https://bokeh-staging.materials.zone/error"
        elif env == 'production':
            return "https://bokeh.materials.zone/error"
