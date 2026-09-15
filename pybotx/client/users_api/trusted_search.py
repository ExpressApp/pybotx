def validate_trusted_search_options(
    *,
    trusts_search: bool,
    partial_response: bool,
) -> None:
    if partial_response and not trusts_search:
        raise ValueError("`partial_response=True` requires `trusts_search=True`")
