__all__ = (
    "AsyncBufferBase",
    "AsyncBufferReadable",
    "AsyncBufferWritable",
    "AttachmentFactoryPort",
    "BotAccessPort",
    "BotAccountsStoragePort",
    "BotXApiPort",
    "CallbackManagerPort",
    "CallbackRepoProto",
    "DedupStorePort",
    "HttpClientError",
    "HttpClientPort",
    "HttpRequest",
    "HttpResponse",
    "HttpStatusError",
    "HttpTimeoutError",
    "HttpTransportError",
    "JwtEncoderPort",
    "JwtVerifierPort",
    "LoggerPort",
    "RetryPolicyPort",
    "WidgetStateStorePort",
    "get_file_size",
)


def __getattr__(name: str):  # type: ignore[override]
    if name == "AsyncBufferBase":
        from pybotx.domain.ports.async_buffer import AsyncBufferBase

        return AsyncBufferBase
    if name == "AsyncBufferReadable":
        from pybotx.domain.ports.async_buffer import AsyncBufferReadable

        return AsyncBufferReadable
    if name == "AsyncBufferWritable":
        from pybotx.domain.ports.async_buffer import AsyncBufferWritable

        return AsyncBufferWritable
    if name == "AttachmentFactoryPort":
        from pybotx.domain.ports.attachment_factory import AttachmentFactoryPort

        return AttachmentFactoryPort
    if name == "get_file_size":
        from pybotx.domain.ports.async_buffer import get_file_size

        return get_file_size
    if name == "BotAccessPort":
        from pybotx.domain.ports.bot_access import BotAccessPort

        return BotAccessPort
    if name == "BotAccountsStoragePort":
        from pybotx.domain.ports.bot_accounts_storage import BotAccountsStoragePort

        return BotAccountsStoragePort
    if name == "BotXApiPort":
        from pybotx.domain.ports.botx_api import BotXApiPort

        return BotXApiPort
    if name == "CallbackManagerPort":
        from pybotx.domain.ports.callback_manager import CallbackManagerPort

        return CallbackManagerPort
    if name == "CallbackRepoProto":
        from pybotx.domain.ports.callback_repo import CallbackRepoProto

        return CallbackRepoProto
    if name == "DedupStorePort":
        from pybotx.domain.ports.dedup_store import DedupStorePort

        return DedupStorePort
    if name == "HttpClientPort":
        from pybotx.domain.ports.http_client import HttpClientPort

        return HttpClientPort
    if name == "HttpRequest":
        from pybotx.domain.ports.http_client import HttpRequest

        return HttpRequest
    if name == "HttpResponse":
        from pybotx.domain.ports.http_client import HttpResponse

        return HttpResponse
    if name == "HttpClientError":
        from pybotx.domain.ports.http_client import HttpClientError

        return HttpClientError
    if name == "HttpTransportError":
        from pybotx.domain.ports.http_client import HttpTransportError

        return HttpTransportError
    if name == "HttpTimeoutError":
        from pybotx.domain.ports.http_client import HttpTimeoutError

        return HttpTimeoutError
    if name == "HttpStatusError":
        from pybotx.domain.ports.http_client import HttpStatusError

        return HttpStatusError
    if name == "JwtEncoderPort":
        from pybotx.domain.ports.jwt_encoder import JwtEncoderPort

        return JwtEncoderPort
    if name == "JwtVerifierPort":
        from pybotx.domain.ports.jwt_verifier import JwtVerifierPort

        return JwtVerifierPort
    if name == "LoggerPort":
        from pybotx.domain.ports.logger import LoggerPort

        return LoggerPort
    if name == "RetryPolicyPort":
        from pybotx.domain.ports.retry_policy import RetryPolicyPort

        return RetryPolicyPort
    if name == "WidgetStateStorePort":
        from pybotx.domain.ports.widget_state_store import WidgetStateStorePort

        return WidgetStateStorePort
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
