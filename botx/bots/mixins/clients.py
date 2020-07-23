"""Define Mixin that combines API and sending mixins and will be used in Bot."""
from typing import List

from botx.bots.mixins.requests.mixin import BotXRequestsMixin
from botx.bots.mixins.sending import SendingMixin
from botx.exceptions import ServerUnknownError
from botx.models.credentials import ExpressServer


class ClientsMixin(SendingMixin, BotXRequestsMixin):
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
        """Search token in bot saved tokens.

        Arguments:
            host: host for which token should be searched.

        Returns:
            Found token.

        Raises:
            ValueError: raised of there is not token for host.
        """
        server = self.get_cts_by_host(host)
        if server.server_credentials is not None:
            return server.server_credentials.token

        raise ValueError("token for cts {0} unfilled".format(host))
