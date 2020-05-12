"""Define Mixin that combines API and sending mixins and will be used in Bot."""
from typing import List

from botx.bots.clients.api import APIMixin
from botx.bots.clients.sending import SendingMixin
from botx.exceptions import ServerUnknownError
from botx.models.credentials import ExpressServer


class ClientsMixin(SendingMixin, APIMixin):
    """Mixin that defines methods that are used for communicating with BotX API."""

    known_hosts: List[ExpressServer]

    def get_cts_by_host(self, host: str) -> ExpressServer:
        """Find CTS in bot registered servers.

        Arguments:
            host: host of server that should be found.

        Returns:
            Found instance of registered server.

        Raises:
            ServerUnknownError: raised if server was not found.
        """
        for cts in self.known_hosts:
            if cts.host == host:
                return cts

        raise ServerUnknownError(host=host)

    def get_token_for_cts(self, host: str) -> str:
        server = self.get_cts_by_host(host)
        if server.server_credentials is not None:
            return server.server_credentials.token

        raise ValueError(f"token for cts {host} unfilled")
