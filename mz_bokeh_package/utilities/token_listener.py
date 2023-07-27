import json
from dataclasses import dataclass
from bokeh.io import curdoc


@dataclass
class Message:
    event: str
    payload: str


class TokenListener:
    """ A static class responsible for listening to messages and updating an internal token value.

    Methods:
        start_listening(): Starts listening for messages using the `curdoc().on_message` method
            to registers and handle "message" events.

        get_token(): Retrieves the current authentication token.
    """
    _token: str | None = None

    @staticmethod
    def start_listening():
        """ Start listening for messages and register the internal event handler for "message" events. """
        curdoc().on_message("message", TokenListener._on_message)

    @staticmethod
    def get_token() -> str:
        """ Get the current authentication token. """
        return TokenListener._token

    @staticmethod
    def _on_message(message: str):
        """ Event handler method called when a new message is received.

        Args:
            message: The incoming message in JSON format.
        """
        message = Message(**json.loads(message))
        if message.event == "AUTH_TOKEN_UPDATE":
            TokenListener._token = message.payload
