import inspect
import re
from typing import Callable, Optional, Union, Sequence, Any, List

from botx import converters
from botx.dependencies import models as deps
from botx.dependencies.solving import get_executor
from botx.models import messages


def get_body_from_name(name: str) -> str:
    """Get auto body from given handler name in format `/word-word`.

    Examples:
        ```
        >>> get_body_from_name("HandlerFunction")
        "handler-function"
        >>> get_body_from_name("handlerFunction")
        "handler-function"
        ```
    Arguments:
        name: name of handler for which body should be generated.
    """
    splited_words = re.findall(r"^[a-z\d_\-]+|[A-Z\d_\-][^A-Z\d_\-]*", name)
    joined_body = "-".join(splited_words)
    dashed_body = joined_body.replace("_", "-")
    return "/{0}".format(re.sub(r"-+", "-", dashed_body).lower())


class Handler:
    """Handler that will store body and callable."""

    def __init__(
        self,
        body: str,
        handler: Callable,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        full_description: Optional[str] = None,
        include_in_status: Union[bool, Callable] = True,
        dependencies: Optional[Sequence[deps.Depends]] = None,
        dependency_overrides_provider: Any = None,
    ) -> None:
        """Init handler that will be used for executing registered logic.

        Arguments:
            handler: callable that will be used for executing handler.
            body: body template that will trigger this handler.
            name: optional name for handler that will be used in generating body.
            description: description for command that will be shown in bot's menu.
            full_description: full description that can be used for example in `/help`
                command.
            include_in_status: should this handler be shown in bot's menu, can be
                callable function with no arguments *(for now)*.
            dependencies: sequence of dependencies that should be executed before
                handler.
            dependency_overrides_provider: mock of callable for handler.
        """
        if include_in_status:
            assert body.startswith(
                '/',
            ), "Public commands should start with leading slash"
            assert (
                body[: -len(body.strip('/'))].count('/') == 1
            ), "Command body can contain only single leading slash"
            assert (
                len(body.split()) == 1
            ), "Public commands should contain only one word"

        self.body: str = body
        """Command body."""
        self.handler: Callable = handler
        """Callable for executing registered logic."""
        self.name: str = get_name_from_callable(handler) if name is None else name
        """Name of handler."""

        self.dependencies: List[deps.Depends] = converters.optional_sequence_to_list(
            dependencies,
        )
        """Additional dependencies of handler."""
        self.description: Optional[str] = description
        """Description that will be used in bot's menu."""
        self.full_description: str = full_description or inspect.cleandoc(
            handler.__doc__ or "",
        )
        """Extra description."""
        self.include_in_status: Union[bool, Callable] = include_in_status
        """Flag or function that will check if command should be showed in menu."""

        assert inspect.isfunction(handler) or inspect.ismethod(
            handler,
        ), f"Handler must be a function or method"
        self.dependant: deps.Dependant = deps.get_dependant(call=self.handler)
        """Dependency for passed handler."""
        for index, depends in enumerate(self.dependencies):
            assert callable(
                depends.dependency,
            ), "A parameter-less dependency must have a callable dependency"
            self.dependant.dependencies.insert(
                index,
                deps.get_dependant(
                    call=depends.dependency, use_cache=depends.use_cache,
                ),
            )
        self.dependency_overrides_provider: Any = dependency_overrides_provider
        """Overrider for passed dependencies."""
        self.executor: Callable = get_executor(
            dependant=self.dependant,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )
        """Main logic executor for passed handler."""

    def matches(self, message: messages.Message) -> bool:
        """Check if message body matched to handler's body.

        Arguments:
            message: incoming message which body will be used to check route.
        """
        return bool(re.compile(self.body).match(message.body))

    def command_for(self, *args: Any) -> str:
        """Build a command string using passed body params.

        Arguments:
            args: sequence of elements that are arguments for command.
        """
        args_str = " ".join((str(arg) for arg in args[1:]))
        return "{0} {1}".format(self.body, args_str).strip()

    async def __call__(self, message: messages.Message) -> None:
        """Execute handler using incoming message.

        Arguments:
            message: message that will be handled by handler.
        """
        await self.executor(message)

    def __eq__(self, other: object) -> bool:
        """Compare 2 handlers for equality.

        Arguments:
            other: handler to compare with.

        Returns:
            Result of comparing.
        """

        if not isinstance(other, Handler):
            return False

        callable_comp = self.handler == other.handler
        callable_comp = callable_comp and self.dependencies == other.dependencies

        export_comp = self.name == other.name
        export_comp = export_comp and self.body == other.body
        export_comp = export_comp and self.description == other.description
        export_comp = export_comp and self.full_description == other.full_description
        export_comp = export_comp and self.include_in_status == other.include_in_status

        return callable_comp and export_comp


def get_name_from_callable(handler: Callable) -> str:
    """Get auto name from given callable object.

    Arguments:
        handler: callable object that will be used to retrieve auto name for handler.

    Returns:
        Name obtained from callable.
    """
    is_function = inspect.isfunction(handler)
    is_method = inspect.ismethod(handler)
    is_class = inspect.isclass(handler)
    if is_function or is_method or is_class:
        return handler.__name__
    return handler.__class__.__name__