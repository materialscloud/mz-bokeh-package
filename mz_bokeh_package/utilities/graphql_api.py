from __future__ import annotations  # to support internal types as type hints

import logging
from functools import lru_cache
from dataclasses import dataclass

from jsonschema import validate, ValidationError
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport, log as requests_logger

from mz_bokeh_package.utilities import CurrentUser, Environment

requests_logger.setLevel(logging.WARNING)


@dataclass
class User:
    id: str = ""
    name: str = ""


class GraphqlQueryError(Exception):
    """ This exception is raised when an error occurred in a GraphQL query. """
    pass


class MZGraphQLClient:

    def __init__(self):

        self._client = self._get_gql_client()

    @lru_cache()
    def get_user(self) -> User | None:
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
                "user": {
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

        result = self._client.execute(query)

        try:
            validate(result, schema=result_schema)
        except ValidationError as e:
            raise GraphqlQueryError(f"invalid result of GraphQL query for getting the user's organization ID. "
                                    f"Validation error: {e.message}")

        if not result['user']:
            return None
        else:
            return User(id=result['user']['id'], name=result['user']['name'])

    @staticmethod
    def _get_gql_client() -> Client:
        """get a graphql client with the appropriate authorization header for the current user

        Returns:
            GraphQL client
        """
        transport = RequestsHTTPTransport(url=Environment.get_graphql_api_url(), verify=True, retries=3)
        client = Client(transport=transport)

        client.transport.headers = {"authorization": f"API {CurrentUser.get_api_key()}"}
        return client
