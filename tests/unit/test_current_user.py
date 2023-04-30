import pytest
from bokeh.document import Document
from dataclasses import dataclass

from mz_bokeh_package.utilities import CurrentUser
from mz_bokeh_package.utilities import MZGraphQLClient

API_KEY = "6fzQxEJL1YX9ldWUhHv5NPpiIcV7Gg8r03KwmeCqyRakj2nSAstDMTb4oB"
SESSION_ID = "LME0EBfddYQCJqpZoO4ysYvynDXFLavC8hu3RzHW6e5e"
USER_ID = "79e8e0f4-d2d6-4c16-b833-0a8986a6ce53"
USER_NAME = "user_name"


TESTS = [
    # Test 1: session ID provided and is logged in CurrentUser._users. API key not requered.
    {
        "input": {
            "session_active": True,
            "logged_user": True,
            "session_id": SESSION_ID,
            "api_key": None,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
    # Test 2: session ID provided and is not logged in CurrentUser._users. API key provided.
    {
        "input": {
            "session_active": True,
            "logged_user": False,
            "session_id": SESSION_ID,
            "api_key": API_KEY,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
    # Test 3: session ID not provided and is not logged in CurrentUser._users. API key provided.
    {
        "input": {
            "session_active": False,
            "logged_user": False,
            "session_id": None,
            "api_key": API_KEY,
        },
        "output": {"id": USER_ID, "name": USER_NAME}
    },
]


@dataclass
class SessionContext:
    id: str = ""


@pytest.mark.parametrize("parameters", TESTS)
def test_get_user_info(monkeypatch, parameters: dict):
    CurrentUser._users = {}
    session_active = parameters['input']['session_active']
    logged_user = parameters['input']['logged_user']
    session_id = parameters['input']['session_id']
    api_key = parameters['input']['api_key']
    expected_output = parameters['output']

    if session_active and logged_user:
        session_context = SessionContext(id=session_id)
        CurrentUser._users[session_id] = expected_output
    elif session_active:
        session_context = SessionContext(id=session_id)
    else:
        session_context = None

    monkeypatch.setattr(Document, "session_context", session_context)
    monkeypatch.setattr(CurrentUser, "get_api_key", lambda: api_key)
    monkeypatch.setattr(MZGraphQLClient, "_get_gql_client", lambda cls_object: None)
    monkeypatch.setattr(
        MZGraphQLClient,
        "get_user",
        lambda cls_object, api_key_input: {"id": USER_ID, "name": USER_NAME} if api_key_input else None
    )

    try:
        user_info = CurrentUser.get_user_info(api_key)
    except Exception as e:
        user_info = type(e)
    finally:
        assert user_info == expected_output


def test_get_user_info_error():
    """
    Test that CurrentUser.get_user_info raises a ValueError when no session ID, no CurrentUser._users is cashed, and
    no API key is provided.

    Raises:
        ValueError: If both session ID and API key are not provided.
    """
    with pytest.raises(ValueError):
        CurrentUser.get_user_info(None)
