def get_api_key_from_query_arguments(query_arguments: dict) -> str | None:
    """Get API key from the provided query arguments.

    Args:
        query_arguments: A dictionary containing query arguments.

    Returns:
        The API key if found in the query arguments and only one is present, otherwise None.
    """

    api_keys = query_arguments.get("api_key")
    if api_keys is not None and len(api_keys) == 1:
        api_key = api_keys[0]
        if isinstance(api_key, bytes):
            api_key = api_key.decode('utf8')
        return api_key
    else:
        return None

def get_auth_token_from_query_arguments(query_arguments: dict) -> str | None:
    """Get auth token from the provided query arguments.

    Args:
        query_arguments: A dictionary containing query arguments.

    Returns:
        The auth token if found in the query arguments and only one is present, otherwise None.
    """

    auth_tokens = query_arguments.get("auth_token")
    if auth_tokens is not None and len(auth_tokens) == 1:
        auth_token = auth_tokens[0]
        if isinstance(auth_token, bytes):
            auth_token = auth_token.decode('utf8')
        return auth_token
    else:
        return None
