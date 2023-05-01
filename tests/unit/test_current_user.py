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
            "session_id": {"id": USER_ID, "name": USER_NAME},
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
            "session_id": {"id": USER_ID, "name": USER_NAME},
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
            "session_id": {"id": USER_ID, "name": USER_NAME},
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
            "session_id": {"id": USER_ID, "name": USER_NAME},
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
            "session_id": {"id": USER_ID, "name": USER_NAME},
            "users_cache": {},
        },
    },
]


@pytest.mark.parametrize("parameters", TESTS_PASS)
def test_get_user_info(monkeypatch, parameters: dict):

    session_id = parameters["input"]["session_id"]
    monkeypatch.setattr(CurrentUser, "_get_session_id", lambda: session_id)

    users_cache = parameters["input"]["users_cache"]
    monkeypatch.setattr(CurrentUser, "_users_cache", users_cache)

    get_api_key = parameters["input"]["get_api_key"]
    monkeypatch.setattr(CurrentUser, "get_api_key", lambda: get_api_key)

    get_user = parameters["input"]["get_user"]
    monkeypatch.setattr(MZGraphQLClient, "get_user", lambda api_key: get_user)

    user_info = CurrentUser._get_user_info(parameters['input']['api_key'])
    assert user_info == parameters['output']["session_id"]
    assert CurrentUser._users_cache == parameters['output']["users_cache"]


def test_get_user_info_error():
    """Test that CurrentUser.get_user_info raises a ValueError when no session ID, no CurrentUser._users_cache is cashed, and
    no API key is provided.
    """
    with pytest.raises(FetchUserInfoError):
        CurrentUser._get_user_info(None)
