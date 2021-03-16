"""
This module contains functions for obtaining environment (e.g. dev/staging/production) specific data

"""

import os


def get_environment() -> str:
    """get the current environment

    Returns:
        the current environment, possible values are: 'dev', 'staging' or 'production'
    """

    # in the kubernetes deployed containers, the environemnt variable ENVIRONMENT is set to staging/production
    return os.getenv('ENVIRONMENT', 'dev')


def get_request_url(endpoint: str) -> str:
    """receives an endpoint of an API request and converts it to a request url based on the environment

    Args:
        endpoint: the endpoint of the request

    Returns:
        the full URL of the request
    """

    env = get_environment()

    if env == 'staging':
        host = 'staging.materials.zone:5000'
    elif env == 'production':
        host = 'production.materials.zone:5000'
    elif env == 'dev':
        host = os.getenv('API_HOST', 'staging.materials.zone:5000')
    else:
        host = "error"

    return f"http://{host}/{endpoint}"


def get_error_page_url() -> str:
    """get the url for the MaterialsZone app

    Returns:
        the URL of the MaterialsZone app
    """

    env = get_environment()

    if env == 'staging':
        return "https://bokeh-staging.materials.zone/error"
    elif env == 'production':
        return "https://bokeh.materials.zone/error"
    elif env == 'dev':
        return "https://bokeh-staging.materials.zone/error"
    else:
        return "error"


def get_webapp_host() -> str:
    """get the web app host based on the environment.

    Returns:
        str: Web app host.
    """
    env = get_environment()

    if env == "staging":
        return "materials-zone-v2.firebaseapp.com"
    elif env == "production":
        return "app.materials.zone"
    elif env == "dev":
        return os.getenv('WEBAPP_HOST', "materials-zone-v2.firebaseapp.com")
    else:
        return "error"
