"""Dagster Resource exposing a Tinnery Provider.

通过 Tinnery Provider 暴露能力的 Dagster Resource。
"""

from tinnery.core import invoke_flow
from tinnery.evidence import ExecutionEvidence
from tinnery.invocation import InvocationResult
from tinnery.provider import Provider


class TinneryResource:
    """Dagster resource that wraps a Tinnery Provider.

    Host-defined Dagster ops and assets use this resource to invoke Tinnery
    Flows through the same Tinnery Core invocation path as the host CLI.

    宿主自定义的 Dagster op 和 asset 通过该资源，经由与宿主 CLI 相同的
    Tinnery Core 调用路径调用 Tinnery Flow。

    Passed to Dagster as a plain Python object (Dagster wraps it as a
    hardcoded resource at execution time).

    作为普通 Python 对象传入 Dagster（Dagster 在执行时将其包装为硬编码资源）。
    """

    def __init__(self, provider: Provider):
        self.provider = provider

    def invoke(self, request) -> tuple[InvocationResult, ExecutionEvidence]:
        """Invoke a Flow through Tinnery Core.

        通过 Tinnery Core 调用 Flow。
        """
        return invoke_flow(request, self.provider)
