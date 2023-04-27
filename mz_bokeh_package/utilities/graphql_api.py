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
    def get_user(self, api_key: str) -> dict:
        """This method fetches the id and name of a given user.

        Returns:
            User object.
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
                                    "Validation error: result does not contain a viewer.")
        return result['viewer']

    @staticmethod
    def _get_gql_client() -> Client:
        """get a graphql client with the appropriate authorization header for the current user

        Returns:
            GraphQL client
        """

        transport = RequestsHTTPTransport(url=Environment.get_graphql_api_url(), verify=True, retries=3)
        client = Client(transport=transport)

        return client
