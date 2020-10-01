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
        mz_app_url = "https://bokeh-staging.materials.zone/error"
    elif env == 'production':
        mz_app_url = "https://bokeh.materials.zone/error"
    elif env == 'dev':
        mz_app_url = "https://bokeh-staging.materials.zone/error"
    else:
        mz_app_url = "error"

    return mz_app_url


def get_db_host() -> str:
    """Returns a database host address based on the current environment

    The database is a Postgres database running on GCP.

    Returns:
        str: Database host address
    """
    STAGING_HOST = "35.233.124.184"
    PRODUCTION_HOST = "104.199.26.69"

    env = get_environment()

    if env == 'staging':
        host = STAGING_HOST
    elif env == 'production':
        host = PRODUCTION_HOST
    elif env == 'dev':
        host = os.getenv('DB_HOST', STAGING_HOST)
    else:
        host = "error"

    return host
