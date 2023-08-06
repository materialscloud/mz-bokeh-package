import pytest

from mz_bokeh_package.utilities import CurrentUser, FetchUserInfoError
from mz_bokeh_package.utilities.graphql_api import MZGraphQLClient

API_KEY = "6fzQxEJL"
TOKEN = "eyJhbGciO"
SESSION_ID = "pZoO4ysY"
USER_ID = "79e8e0f4"
USER_NAME = "user_name"


TESTS_PASS = [
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME, "token": TOKEN,}},
            "get_api_key": None,
            "get_token": None,
            "get_user": None

        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME, "token": TOKEN},
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME, "token": TOKEN}}
        },
    },
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {},
            "get_api_key": API_KEY,
            "get_token": TOKEN,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME, "token": TOKEN},
            "users_cache": {SESSION_ID: {"id": USER_ID,"name": USER_NAME, "token": TOKEN}}
        },
    },
    {
        "input": {
            "session_id": None,
            "users_cache": {},
            "get_api_key": API_KEY,
            "get_token": TOKEN,
            "get_user": {"id": USER_ID, "name": USER_NAME}
        },
        "output": {
            "user_info": {"id": USER_ID, "name": USER_NAME, "token": TOKEN},
            "users_cache": {},
        },
    },
]


TESTS_FAILURE = [
    {
        "input": {
            "session_id": None,
            "users_cache": {},
            "get_api_key": None,
            "get_token": None,
            "get_user": None
        },
        "output": {
            "error": FetchUserInfoError,
        },
    },
    {
        "input": {
            "session_id": SESSION_ID,
            "users_cache": {},
            "get_api_key": None,
            "get_token": None,
            "get_user": None
        },
        "output": {
            "error": FetchUserInfoError,
        },
    },
    {
        "input": {
            "session_id": None,
            "users_cache": {SESSION_ID: {"id": USER_ID, "name": USER_NAME, "token": TOKEN}},
            "get_api_key": None,
            "get_token": None,
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

    get_token = parameters["input"]["get_token"]
    monkeypatch.setattr(CurrentUser, "get_token", lambda: get_token)

    _get_initial_token = parameters["input"]["get_token"]
    monkeypatch.setattr(CurrentUser, "_get_initial_token", lambda: _get_initial_token)

    get_user = parameters["input"]["get_user"]
    monkeypatch.setattr(MZGraphQLClient, "get_user", lambda api_key, token: get_user)

    return parameters


@pytest.mark.parametrize("monkeypatch_parameters", TESTS_PASS, indirect=["monkeypatch_parameters"])
def test_get_user_info_pass(monkeypatch_parameters):
    user_info = CurrentUser._get_user_info()
    assert user_info == monkeypatch_parameters['output']["user_info"]
    assert CurrentUser._users_cache == monkeypatch_parameters['output']["users_cache"]


@pytest.mark.parametrize("monkeypatch_parameters", TESTS_FAILURE, indirect=["monkeypatch_parameters"])
def test_get_user_info_error(monkeypatch_parameters):
    with pytest.raises(monkeypatch_parameters['output']["error"]):
        CurrentUser._get_user_info()
