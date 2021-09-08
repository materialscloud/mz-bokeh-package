import os
import pytest

from typing import Callable, Optional

from mz_bokeh_package.utilities import Environment

staging_url = 'https://api-staging.materials.zone/v1beta1' + '/'
production_url = 'https://api.materials.zone/v1beta1' + '/'
custom_api_host_url = 'http://staging.materials.zone:5000' + '/'

# The order of the tests is important. set_env_to_development_with_own_host sets the environment variable
# API_HOST which is expected not to be set for the other test.
test_parameters = [("staging", staging_url, None),
                   ("production", production_url, None),
                   ("dev", staging_url, None),
                   ("dev", custom_api_host_url, custom_api_host_url[:-1])]


@pytest.mark.parametrize('environment, expected_url, custom_api_host', test_parameters)
def test_environment(environment: Callable, expected_url: str, custom_api_host: Optional[str]) -> None:
    os.environ['ENVIRONMENT'] = environment
    if custom_api_host is not None:
        os.environ['API_HOST'] = custom_api_host

    assert Environment.get_request_url("") == expected_url
    assert Environment.get_request_url("test") == expected_url + "test"
