import os
import pytest

from typing import Optional

from mz_bokeh_package.utilities import Environment

external_api_url_staging = 'https://api-staging.materials.zone/v1beta1/'
external_api_url_production = 'https://api.materials.zone/v1beta1/'

graphql_api_url_staging = 'https://api-staging.materials.zone/graphql'
graphql_api_url_production = 'https://api.materials.zone/graphql'

app_url_staging = 'https://app-staging.materials.zone'
app_url_production = 'https://app.materials.zone'

error_url_staging = 'https://bokeh-staging.materials.zone/error'
error_url_production = 'https://bokeh.materials.zone/error'

custom_host_url = 'http://example.com/'  # This can be any string ending on '/'

# Parameters for testing GET_ENVIRONMENT are:
# 1. os-environmental variable "ENVIRONMENT" to be set or None
# 2. expected reply from get_environment
# 3. expected exception
test_parameters_get_environment = [
    ("staging", "staging", None),
    ("production", "production", None),
    ("dev", "dev", None),
    (None, "dev", None),
    ("Faulty", "Nothing", ValueError),
]

# Parameters for testing GET_REQUEST_URL are:
# 1.os-environmental variable to be set or None
# 2. expected reply
# 3. Optional custom url for dev. environment.
test_parameters_get_request_url = [
    ("staging", external_api_url_staging, None),
    ("production", external_api_url_production, None),
    ("dev", custom_host_url, custom_host_url[:-1]),
    ("dev", external_api_url_staging, None),
    (None, custom_host_url, custom_host_url[:-1]),
    (None, external_api_url_staging, None),
]

test_parameters_get_graphql_api_url = [
    ("staging", graphql_api_url_staging, None),
    ("production", graphql_api_url_production, None),
    ("dev", custom_host_url, custom_host_url),
    ("dev", graphql_api_url_staging, None),
    (None, custom_host_url, custom_host_url),
    (None, graphql_api_url_staging, None),
]

test_parameters_get_error_page_url = [
    ("staging", "https://bokeh-staging.materials.zone/error"),
    ("dev", "https://bokeh-staging.materials.zone/error"),
    (None, "https://bokeh-staging.materials.zone/error"),
    ("production", "https://bokeh.materials.zone/error"),
]

# Parameters for testing GET_WEBAPP_HOST are:
# 1.os-environmental variable to be set or None
# 2. expected reply
# 3. Optional custom url for dev. environment.
test_parameters_get_webapp_host = [
    ("staging", app_url_staging, None),
    ("production", app_url_production, None),
    ("dev", custom_host_url[:-1], custom_host_url[:-1]),
    ("dev", app_url_staging, None),
    (None, custom_host_url[:-1], custom_host_url[:-1]),
    (None, app_url_staging, None),
]


def set_environment(environment: Optional[str]) -> None:
    if environment is None and 'ENVIRONMENT' in os.environ:
        del os.environ['ENVIRONMENT']
    elif environment is not None:
        os.environ['ENVIRONMENT'] = environment


@pytest.mark.parametrize("environment_set, environment_expected, expected_exception", test_parameters_get_environment)
def test_get_environment(environment_set: Optional[str], environment_expected: str, expected_exception) -> None:
    set_environment(environment_set)

    if expected_exception is not None:
        with pytest.raises(expected_exception, match=f".*{environment_set}.*"):
            Environment.get_environment()
    else:
        assert Environment.get_environment() == environment_expected


@pytest.mark.parametrize('environment, expected_url, custom_api_host', test_parameters_get_request_url)
def test_get_request_url(environment: str, expected_url: str, custom_api_host: Optional[str]) -> None:
    set_environment(environment)

    if 'API_HOST' in os.environ:
        del os.environ['API_HOST']
    if custom_api_host is not None:
        os.environ['API_HOST'] = custom_api_host

    assert Environment.get_request_url("") == expected_url
    assert Environment.get_request_url("test") == expected_url + "test"


@pytest.mark.parametrize('environment, expected_url, custom_api_host', test_parameters_get_graphql_api_url)
def test_get_graphql_api_url(environment: str, expected_url: str, custom_api_host: Optional[str]) -> None:
    set_environment(environment)

    if 'GRAPHQL_API_HOST' in os.environ:
        del os.environ['GRAPHQL_API_HOST']
    if custom_api_host is not None:
        os.environ['GRAPHQL_API_HOST'] = custom_api_host

    assert Environment.get_graphql_api_url() == expected_url


@pytest.mark.parametrize('environment_set, expected_url', test_parameters_get_error_page_url)
def test_get_error_page_url(environment_set: Optional[str], expected_url: str) -> None:
    set_environment(environment_set)

    assert Environment.get_error_page_url() == expected_url


@pytest.mark.parametrize('environment, expected_url, custom_api_host', test_parameters_get_webapp_host)
def test_get_webapp_host(environment: str, expected_url: str, custom_api_host: Optional[str]) -> None:
    set_environment(environment)

    if 'WEBAPP_HOST' in os.environ:
        del os.environ['WEBAPP_HOST']
    if custom_api_host is not None:
        os.environ['WEBAPP_HOST'] = custom_api_host

    assert Environment.get_webapp_host() == expected_url
