from __future__ import annotations  # to support internal types as type hints

import logging
from functools import lru_cache

from jsonschema import validate, ValidationError
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport, log as requests_logger

from mz_bokeh_package.utilities.environment import Environment

requests_logger.setLevel(logging.WARNING)


class GraphqlQueryError(Exception):
    """ This exception is raised when an error occurred in a GraphQL query. """
    pass


class MZGraphQLClient:

    def __init__(self):

        self._client = self._get_gql_client()

    @lru_cache()
    def get_user(self, api_key: str) -> dict[str, str]:
        """Gets the ID and name of the currently active viewer using a valid API key.

        Args:
            api_key: The API key to use for the API call.

        Returns:
            A dictionary with the following keys:
            - id: The ID of the user.
            - name: The name of the user.
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
                    "required": ["id", "name"],
                    "additionalProperties": False,
                },
            },
        }

        self._client.transport.headers = {"authorization": f"API {api_key}"}
        result = self._client.execute(query)

        try:
            validate(result, schema=result_schema)
        except ValidationError as e:
            raise GraphqlQueryError(f"invalid result of GraphQL query for getting the user's organization ID and name. "
                                    f"Validation error: {e.message}")

        if "viewer" not in result:
            raise GraphqlQueryError("invalid result of GraphQL query for getting the user's organization ID and name. "
                                    "Validation error: 'viewer' field not found. The provided API key may be invalid"
                                    "or expired.")
        return result['viewer']

    @staticmethod
    def _get_gql_client() -> Client:
        """Get a graphql client with the appropriate authorization header for the current user

        Returns:
            GraphQL client
        """

        transport = RequestsHTTPTransport(url=Environment.get_graphql_api_url(), verify=True, retries=3)
        client = Client(transport=transport)

        return client
