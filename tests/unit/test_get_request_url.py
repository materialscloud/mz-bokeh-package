import os
import pytest

from typing import Callable, Optional

from mz_bokeh_package.utilities import Environment

staging_url = 'https://api-staging.materials.zone/v1beta1' + '/'
production_url = 'https://api.materials.zone/v1beta1' + '/'
custom_api_host_url = 'http://staging.materials.zone:5000' + '/'

test_parameters = [("staging", staging_url, None),
                   ("production", production_url, None),
                   ("dev", custom_api_host_url, custom_api_host_url[:-1]),
                   ("dev", staging_url, None),
                   ]


@pytest.mark.parametrize('environment, expected_url, custom_api_host', test_parameters)
def test_environment(environment: Callable, expected_url: str, custom_api_host: Optional[str]) -> None:
    os.environ['ENVIRONMENT'] = environment

    if 'API_HOST' in os.environ:
        del os.environ['API_HOST']
    if custom_api_host is not None:
        os.environ['API_HOST'] = custom_api_host

    assert Environment.get_request_url("") == expected_url
    assert Environment.get_request_url("test") == expected_url + "test"
