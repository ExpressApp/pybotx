import pybotx.domain.ports as ports


def test__ports_lazy_imports() -> None:
    assert ports.LoggerPort is not None
    assert ports.RetryPolicyPort is not None
