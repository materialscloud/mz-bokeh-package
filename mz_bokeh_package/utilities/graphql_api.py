from __future__ import annotations  # to support internal types as type hints

import logging

from jsonschema import validate, ValidationError
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport, log as requests_logger
from requests.exceptions import RetryError

from .environment import Environment

requests_logger.setLevel(logging.WARNING)


class GraphqlQueryError(Exception):
    """ This exception is raised when an error occurred in a GraphQL query. """
    pass


class MZGraphQLClient:

    @staticmethod
    def get_user(api_key: str) -> dict[str, str]:
        """Gets the ID and name of the currently active viewer using a valid API key.

        Args:
            api_key: The API key to use for the API call.

        Returns:
            a dictionary containing the user id and name corresponding to the user with this api_key:
            {"id": <user id>, "name": <user name>}
        """

        query = gql(
            """
            query Viewer {
                viewer {
                    id
                    name
                }
            }
            """
        )

        result_schema = {
            "type": "object",
            "properties": {
                "viewer": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                    },
                    "required": ["id", "name"]
                }
            },
            "required": ["viewer"],
            "additionalProperties": False
        }

        client = MZGraphQLClient._get_gql_client(api_key)

        try:
            result = client.execute(query)
        except RetryError as e:
            raise GraphqlQueryError(f"invalid result of the viewer GraphQL query. The provided API key may be invalid "
                                    f"Retry error: {e}")

        try:
            validate(result, schema=result_schema)
        except ValidationError as e:
            raise GraphqlQueryError(f"invalid result of the viewer GraphQL query. "
                                    f"Validation error: {e}")

        return result['viewer']

    @staticmethod
    def _get_gql_client(api_key: str) -> Client:
        """Get a graphql client with the appropriate authorization header for the current user.

        Args:
            api_key: The API key to use for the API call.

        Returns:
            GraphQL client
        """

        transport = RequestsHTTPTransport(url=Environment.get_graphql_api_url(), verify=True, retries=3)
        client = Client(transport=transport)
        client.transport.headers = {"authorization": f"API {api_key}"}

        return client
