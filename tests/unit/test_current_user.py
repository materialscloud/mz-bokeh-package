import pytest

from mz_bokeh_package.utilities import CurrentUser
from mz_bokeh_package.utilities import MZGraphQLClient

API_KEY = "6fzQxEJL1YX9ldWUhHv5NPpiIcV7Gg8r03KwmeCqyRakj2nSAstDMTb4oB"
SESSION_ID = "LME0EBfddYQCJqpZoO4ysYvynDXFLavC8hu3RzHW6e5e"
USER_ID = "79e8e0f4-d2d6-4c16-b833-0a8986a6ce53"
USER_NAME = "user_name"


TESTS = [
    # Test 1: session ID provided and is cached in CurrentUser._users. API key not required.
    {
        "input": {
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME}},
            "api_key": None,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
    # Test 2: session ID provided and is not cached in CurrentUser._users. API key provided.
    {
        "input": {
            "users_cache": {SESSION_ID: {}},
            "api_key": API_KEY,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
    # Test 3: session ID not provided and is not cached in CurrentUser._users. API key provided.
    {
        "input": {
            "users_cache": {},
            "api_key": API_KEY,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
]


@pytest.mark.parametrize("parameters", TESTS)
def test_get_user_info(monkeypatch, parameters: dict):

    session_id = next(iter(parameters["input"]["users_cache"]), None)
    monkeypatch.setattr(CurrentUser, "_get_session_id", lambda: session_id)

    users_cache = parameters["input"]["users_cache"]
    monkeypatch.setattr(CurrentUser, "_users", users_cache if any(users_cache.values()) else {})

    monkeypatch.setattr(MZGraphQLClient, "_get_gql_client", lambda cls_object: None)
    monkeypatch.setattr(MZGraphQLClient, "get_user", _get_user)

    user_info = CurrentUser.get_user_info(parameters['input']['api_key'])
    assert user_info == parameters['output']


def test_get_user_info_error():
    """
    Test that CurrentUser.get_user_info raises a ValueError when no session ID, no CurrentUser._users is cashed, and
    no API key is provided.

    Raises:
        ValueError: If both session ID and API key are not provided.
    """
    with pytest.raises(ValueError):
        CurrentUser.get_user_info(None)


def _get_user(cls_object, api_key_input):
    if api_key_input:
        return {"id": USER_ID, "name": USER_NAME}
    else:
        return None
