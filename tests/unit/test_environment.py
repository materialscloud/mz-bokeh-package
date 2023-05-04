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

test_parameters_get_error_page_url = [
    ("staging", "https://bokeh-staging.materials.zone/error"),
    ("dev", "https://bokeh-staging.materials.zone/error"),
    (None, "https://bokeh-staging.materials.zone/error"),
    ("production", "https://bokeh.materials.zone/error"),
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


def test_get_request_url():
    if 'API_HOST' in os.environ:
        del os.environ['API_HOST']
    os.environ['API_HOST'] = "api.host"

    assert Environment.get_request_url("endpoint") == "api.host" + "/endpoint"


def test_get_graphql_api_url():
    if 'GRAPHQL_API_HOST' in os.environ:
        del os.environ['GRAPHQL_API_HOST']
    os.environ['GRAPHQL_API_HOST'] = "graphql.api.host"

    assert Environment.get_graphql_api_url() == "graphql.api.host"


def test_get_webapp_host():
    if 'WEBAPP_HOST' in os.environ:
        del os.environ['WEBAPP_HOST']
    os.environ['WEBAPP_HOST'] = "webapp.host"

    assert Environment.get_webapp_host() == "webapp.host"
