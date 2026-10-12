"""Dagster Op mapping for Tinnery Flow invocations.

Tinnery Flow 调用到 Dagster Op 的映射。
"""

import re
from typing import Any

from dagster import op

from tinnery.evidence import EvidenceJournal
from tinnery.runtime import BoundFlow, Executor


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
    bound_flow: BoundFlow,
    journal: EvidenceJournal | None = None,
    name: str | None = None,
):
    """Build a Dagster op that invokes a Tinnery Flow through Tinnery Core.

    构建通过 Tinnery Core 调用 Tinnery Flow 的 Dagster op。

    The op maps a Dagster run request (op config ``payload``) onto a payload,
    executes the bound host-owned function via ``Executor``, logs the receipt,
    and fails the Dagster step if the invocation did not succeed.

    该 op 将 Dagster 运行请求（op config 的 ``payload``）映射为载荷，经
    ``Executor`` 执行绑定的宿主函数，记录回执，调用未成功时使 Dagster
    step 失败。

    Args:
        bound_flow: A BoundFlow from bind_flow() / bind_flow() 生成的 BoundFlow
        journal: Optional EvidenceJournal for persistence / 可选的持久化日志
        name: Optional op name (derived from flow_id when omitted)
              可选 op 名称（省略时从 flow_id 派生）

    Returns:
        A Dagster op. Its output is a dict with the ExecutionReceipt;
        its trace_id is ``dagster:<run_id>``.
        一个 Dagster op。其输出为包含 ExecutionReceipt 的 dict；
        trace_id 为 ``dagster:<run_id>``。
    """
    op_name = name or _sanitize_op_name(bound_flow.contract.flow_id)

    @op(name=op_name, config_schema={"payload": Any})
    def flow_op(context):
        payload = context.op_config.get("payload")
        invocation_id = f"dagster:{context.run_id}"

        executor = Executor(journal)
        invocation = executor.invoke(bound_flow, payload, invocation_id=invocation_id)

        context.log.info(
            "Tinnery receipt: flow=%s status=%s failure=%s impl=%s contract=%s invocation=%s",
            invocation.receipt.flow_id,
            invocation.receipt.status,
            invocation.receipt.failure_code,
            invocation.receipt.implementation_sha256[:16],
            invocation.receipt.contract_sha256[:16],
            invocation.receipt.invocation_id,
        )

        if invocation.receipt.status != "SUCCEEDED":
            raise FlowInvocationFailed(
                f"Flow {bound_flow.contract.flow_id} failed: "
                f"{invocation.receipt.failure_code}"
            )

        return {
            "output": invocation.output,
            "receipt": invocation.receipt,
        }

    return flow_op
