"""Tinnery Dagster integration.

Tinnery 的 Dagster 集成。

Maps Dagster run requests to Tinnery Flow invocations through Tinnery Core.
The Tinnery Core protocol (Flow identity, invocation protocol, evidence)
is independent of Dagster; this package is only one entry point.

经由 Tinnery Core 将 Dagster 运行请求映射为 Tinnery Flow 调用。
Tinnery Core 协议（Flow 身份、调用协议、证据）独立于 Dagster；
本包只是入口之一。

Requires the ``dagster`` optional extra: ``uv sync --extra dagster``.
需要 ``dagster`` 可选依赖：``uv sync --extra dagster``。
"""

from tinnery.dagster.jobs import make_flow_job
from tinnery.dagster.ops import FlowInvocationFailed, make_flow_op
from tinnery.dagster.resources import TinneryResource

__all__ = [
    "TinneryResource",
    "FlowInvocationFailed",
    "make_flow_op",
    "make_flow_job",
]
