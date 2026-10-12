"""Dagster Op mapping for Tinnery Flow invocations.

Tinnery Flow 调用到 Dagster Op 的映射。
"""

import re

from dagster import op

from tinnery.core import create_invocation_request, invoke_flow
from tinnery.identity import FlowIdentity, ImplementationIdentity
from tinnery.provider import Provider


class FlowInvocationFailed(RuntimeError):
    """Raised inside a Dagster op when a Tinnery Flow invocation fails.

    Tinnery Flow 调用失败时在 Dagster op 内部抛出。
    """


def _sanitize_op_name(flow_id: str) -> str:
    """Derive a valid Dagster op name from a Flow id.

    从 Flow id 派生合法的 Dagster op 名称。
    """
    sanitized = re.sub(r"[^0-9A-Za-z_]+", "_", flow_id).strip("_")
    return f"{sanitized}_flow_op"


def make_flow_op(
    flow_identity: FlowIdentity,
    implementation_identity: ImplementationIdentity,
    provider: Provider,
    name: str | None = None,
):
    """Build a Dagster op that invokes a Tinnery Flow through Tinnery Core.

    构建通过 Tinnery Core 调用 Tinnery Flow 的 Dagster op。

    The op maps a Dagster run request (op config ``inputs``) onto a typed
    Tinnery InvocationRequest, executes the host-owned provider, logs the
    execution evidence, and fails the Dagster step if the invocation failed.

    该 op 将 Dagster 运行请求（op config 的 ``inputs``）映射为类型化的
    Tinnery InvocationRequest，执行宿主拥有的 provider，记录执行证据，
    调用失败时使 Dagster step 失败。

    Args:
        flow_identity: Flow identity shared with all other entries
                       与其他入口共享的 Flow 身份
        implementation_identity: Implementation identity of the host-owned code
                                 宿主拥有代码的实现身份
        provider: Provider wrapping the host-owned business implementation
                  包装宿主业务实现的 Provider
        name: Optional op name (derived from flow_id when omitted)
              可选 op 名称（省略时从 flow_id 派生）

    Returns:
        A Dagster op. Its output is a dict with the InvocationResult and
        ExecutionEvidence; its trace_id is ``dagster:<run_id>``.
        一个 Dagster op。其输出为包含 InvocationResult 与 ExecutionEvidence
        的 dict；trace_id 为 ``dagster:<run_id>``。
    """
    op_name = name or _sanitize_op_name(flow_identity.flow_id)

    @op(name=op_name, config_schema={"inputs": dict})
    def flow_op(context):
        inputs = context.op_config.get("inputs") or {}
        trace_id = f"dagster:{context.run_id}"

        request = create_invocation_request(
            flow_identity,
            implementation_identity,
            inputs,
            trace_id=trace_id,
            invoked_by="dagster",
        )
        result, evidence = invoke_flow(request, provider)

        context.log.info(
            "Tinnery evidence: flow=%s impl=%s status=%s invoked_by=%s trace=%s hash=%s",
            evidence.flow_identity,
            evidence.implementation_identity,
            result.status,
            evidence.invoked_by,
            evidence.trace_id,
            evidence.evidence_hash,
        )

        if not result.is_success:
            raise FlowInvocationFailed(
                f"Flow {flow_identity} failed: {result.error}"
            )

        return {
            "invocation_result": result,
            "execution_evidence": evidence,
        }

    return flow_op
