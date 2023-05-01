import pytest

from mz_bokeh_package.utilities import CurrentUser, FetchUserInfoError
from mz_bokeh_package.utilities import MZGraphQLClient

API_KEY = "6fzQxEJL1YX9ldWUhHv5NPpiIcV7Gg8r03KwmeCqyRakj2nSAstDMTb4oB"
SESSION_ID = "LME0EBfddYQCJqpZoO4ysYvynDXFLavC8hu3RzHW6e5e"
USER_ID = "79e8e0f4-d2d6-4c16-b833-0a8986a6ce53"
USER_NAME = "user_name"


TESTS_PASS = [
    # Test 1: session ID provided and is cached in CurrentUser._users_cache. API key not required.
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
            "api_key": None,
            "get_api_key": None,
            "get_user": None

        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
        },
    },
    # # Test 2: session ID provided and is not cached in CurrentUser._users_cache. API key provided as argument.
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {},
            "api_key": API_KEY,
            "get_api_key": None,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
        },
    },
    # Test 3: session ID not provided and is not cached in CurrentUser._users_cache. API key provided as argument.
    {
        "input": {
            "session_id": None,
            "users_cache": {},
            "api_key": API_KEY,
            "get_api_key": None,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {},
        },
    },
    # Test 4: session ID provided and is not cached in CurrentUser._users_cache.
    # API key provided as an environment variable.
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {},
            "api_key": None,
            "get_api_key": API_KEY,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
        },
    },
    # Test 5: session ID not provided and is not cached in CurrentUser._users_cache.
    # API key provided as an environment variable.
    {
        "input": {
            "session_id": None,
            "users_cache": {},
            "api_key": None,
            "get_api_key": API_KEY,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {},
        },
    },
]


TESTS_FAILURE = [
    # Test 1: no session ID, no CurrentUser._users_cache is cashed, and no API key is provided.
    {
        "input": {
            "session_id": None,
            "users_cache": {},
            "api_key": None,
            "get_api_key": None,
            "get_user": None
        },
        "output": {
            "error": FetchUserInfoError,
        },
    },
    # Test 2: session ID provided, no CurrentUser._users_cache is cashed, and no API key is provided.
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {},
            "api_key": None,
            "get_api_key": None,
            "get_user": None
        },
        "output": {
            "error": FetchUserInfoError,
        },
    },
    # Test 3: no session ID, CurrentUser._users_cache is cashed, and no API key is provided.
    {
        "input": {
            "session_id": None,
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
            "api_key": None,
            "get_api_key": None,
            "get_user": None
        },
        "output": {
            "error": FetchUserInfoError,
        },
    },
]


@pytest.fixture(scope="function")
def monkeypatch_parameters(request, monkeypatch):
    parameters = request.param
    session_id = parameters["input"]["session_id"]
    monkeypatch.setattr(CurrentUser, "_get_session_id", lambda: session_id)

    users_cache = parameters["input"]["users_cache"]
    monkeypatch.setattr(CurrentUser, "_users_cache", users_cache)

    get_api_key = parameters["input"]["get_api_key"]
    monkeypatch.setattr(CurrentUser, "get_api_key", lambda: get_api_key)

    get_user = parameters["input"]["get_user"]
    monkeypatch.setattr(MZGraphQLClient, "get_user", lambda api_key: get_user)

    return parameters


@pytest.mark.parametrize(
    "monkeypatch_parameters",
    [param for param in TESTS_PASS],
    indirect=["monkeypatch_parameters"]
)
def test_get_user_info_pass(monkeypatch_parameters):
    user_info = CurrentUser._get_user_info(monkeypatch_parameters['input']['api_key'])
    assert user_info == monkeypatch_parameters['output']["user_info"]
    assert CurrentUser._users_cache == monkeypatch_parameters['output']["users_cache"]


@pytest.mark.parametrize(
    "monkeypatch_parameters",
    [param for param in TESTS_FAILURE],
    indirect=["monkeypatch_parameters"]
)
def test_get_user_info_error(monkeypatch_parameters):
    with pytest.raises(monkeypatch_parameters['output']["error"]):
        CurrentUser._get_user_info(monkeypatch_parameters['input']['api_key'])
