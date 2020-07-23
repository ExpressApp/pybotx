"""Functions for inspecting signatures and parameters."""

import inspect
from typing import Any, Callable, Dict

from pydantic.typing import ForwardRef, evaluate_forwardref


def get_typed_signature(call: Callable) -> inspect.Signature:
    """Get signature for callable function with solving possible annotations.

    Arguments:
        call: callable object that will be used to get signature with annotations.

    Returns:
        Callable signature obtained.
    """
    signature = inspect.signature(call)
    global_namespace = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=dependency_param.name,
            kind=dependency_param.kind,
            default=dependency_param.default,
            annotation=get_typed_annotation(dependency_param, global_namespace),
        )
        for dependency_param in signature.parameters.values()
    ]
    return inspect.Signature(typed_params)


def get_typed_annotation(
    dependency_param: inspect.Parameter, global_namespace: Dict[str, Any],
) -> Any:
    """Solve forward reference annotation for instance of `inspect.Parameter`.

    Arguments:
        dependency_param: instance of `inspect.Parameter` for which possible forward
            annotation will be evaluated.
        global_namespace: dictionary of entities that can be used for evaluating
            forward references.

    Returns:
        Parameter annotation.
    """
    annotation = dependency_param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, global_namespace, global_namespace)
    return annotation
