import os
import pytest

from typing import Optional

from mz_bokeh_package.utilities import Environment

staging_url_api = 'https://api-staging.materials.zone/v1beta1' + '/'
production_url_api = 'https://api.materials.zone/v1beta1' + '/'

staging_url_app = 'https://app-staging.materials.zone'
production_url_app = 'https://app.materials.zone'

staging_url_error = 'https://bokeh-staging.materials.zone/error'
production_url_error = 'https://bokeh.materials.zone/error'

custom_host_url = 'http://example.com' + '/'  # This can be any string ending on '/'

# Parameters for testing GET_ENVIRONMENT are:
# 1. os-environmental variable "ENVIRONMENT" to be set or None
# 2. expected reply from get_environment
# 3. expected exception
test_parameters_get_environment = [("staging", "staging", None),
                                   ("production", "production", None),
                                   ("dev", "dev", None),
                                   (None, "dev", None),
                                   ("Faulty", "Nothing", ValueError)]

# Parameters for testing GET_REQUEST_URL are:
# 1.os-environmental variable to be set or None
# 2. expected reply
# 3. Optional custom url for dev. environment.
test_parameters_get_request_url = [("staging", staging_url_api, None),
                                   ("production", production_url_api, None),
                                   ("dev", custom_host_url, custom_host_url[:-1]),
                                   ("dev", staging_url_api, None),
                                   (None, custom_host_url, custom_host_url[:-1]),
                                   (None, staging_url_api, None),
                                   ]

test_parameters_get_error_page_url = [("staging", "https://bokeh-staging.materials.zone/error"),
                                      ("dev", "https://bokeh-staging.materials.zone/error"),
                                      (None, "https://bokeh-staging.materials.zone/error"),
                                      ("production", "https://bokeh.materials.zone/error")]

# Parameters for testing GET_WEBAPP_HOST are:
# 1.os-environmental variable to be set or None
# 2. expected reply
# 3. Optional custom url for dev. environment.
test_parameters_get_webapp_host = [("staging", staging_url_app, None),
                                   ("production", production_url_app, None),
                                   ("dev", custom_host_url[:-1], custom_host_url[:-1]),
                                   ("dev", staging_url_app, None),
                                   (None, custom_host_url[:-1], custom_host_url[:-1]),
                                   (None, staging_url_app, None),
                                   ]


def set_environment(environment: Optional[str]) -> None:
    if environment is None:
        if 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']
    else:
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
