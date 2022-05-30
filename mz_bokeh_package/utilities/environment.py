"""This module contains functions for obtaining environment (e.g. dev/staging/production) specific data
"""

import os


class Environment:

    @staticmethod
    def get_environment() -> str:
        """get the current environment

        Raises:
            ValueError: Whenever the environment is invalid.

        Returns:
            str: the current environment, possible values are: 'dev', 'staging' or 'production'
        """

        # in the kubernetes deployed containers, the environemnt variable ENVIRONMENT is set to staging/production
        env = os.getenv('ENVIRONMENT', 'dev')

        if env not in {"staging", "production", "dev"}:
            raise ValueError(f'The "{env}" environment is invalid. Valid environments: "staging"/"production"/"dev"')

        return env

    @classmethod
    def get_request_url(cls, endpoint: str) -> str:
        """receives an endpoint of an API request and converts it to a request url based on the environment.
        If the environment variable 'ENVIRONMENT' is set to 'dev' the environment variable 'API_HOST' should
        be set to the desired url, including 'https://'. If 'API_HOST' is not set in the development environment,
        the default staging url will be returned.

        Args:
            endpoint: the endpoint of the request

        Returns:
            the full URL of the request
        """

        env = cls.get_environment()

        if env == 'staging':
            host = 'https://api-staging-wip.materials.zone/v1beta1'
        elif env == 'production':
            host = 'https://api.materials.zone/v1beta1'
        elif env == 'dev':
            host = os.getenv('API_HOST', 'https://api-staging-wip.materials.zone/v1beta1')

        return f"{host}/{endpoint}"

    @classmethod
    def get_parser_service_url(cls, endpoint: str) -> str:
        """receives an endpoint of a Parser Service request and converts it to a request url based on the environment.
        If the environment variable 'ENVIRONMENT' is set to 'dev' the environment variable 'PARSER_SERVICE_HOST' should
        be set to the desired url, including 'https://'. If 'PARSER_SERVICE_HOST' is not set in the development
        environment, the default staging url will be returned.

        Args:
            endpoint: the endpoint of the request

        Returns:
            the full URL of the request
        """

        env = cls.get_environment()

        if env == 'staging':
            host = 'https://parser-service-staging-wip.materials.zone/api/v1beta1'
        elif env == 'production':
            host = 'https://parser-service.materials.zone/api/v1beta1'
        elif env == 'dev':
            host = os.getenv('PARSER_SERVICE_HOST', 'https://parser-service-staging-wip.materials.zone/api/v1beta1')

        return f"{host}/{endpoint}"

    @classmethod
    def get_error_page_url(cls) -> str:
        """get the url for the MaterialsZone app

        Returns:
            the URL of the MaterialsZone app
        """

        env = cls.get_environment()

        if env in {'staging', 'dev'}:
            return "https://bokeh-staging-wip.materials.zone/error"
        elif env == 'production':
            return "https://bokeh.materials.zone/error"

    @classmethod
    def get_webapp_host(cls) -> str:
        """get the web app host based on the environment.

        Returns:
            str: Web app host.
        """
        env = cls.get_environment()

        if env == "staging":
            return "https://app-staging-wip.materials.zone"
        elif env == "production":
            return "https://app.materials.zone"
        elif env == "dev":
            return os.getenv('WEBAPP_HOST', "https://app-staging-wip.materials.zone")
