"""Core invocation logic.

核心调用逻辑。
"""

import uuid
from typing import Any

from tinnery.identity import FlowIdentity, ImplementationIdentity
from tinnery.invocation import InvocationRequest, InvocationResult
from tinnery.provider import Provider
from tinnery.evidence import ExecutionEvidence


def invoke_flow(
    request: InvocationRequest,
    provider: Provider
) -> tuple[InvocationResult, ExecutionEvidence]:
    """Invoke a Flow through a Provider and record execution evidence.

    通过 Provider 调用 Flow 并记录执行证据。

    The provider executes the host-owned business implementation. Provider
    exceptions are captured as a failure InvocationResult so that execution
    evidence exists for both successful and failed invocations. Callers decide
    whether to raise on failure.

    Provider 执行宿主拥有的实际业务实现。Provider 异常会被捕获为失败的
    InvocationResult，使成功与失败的调用都存在执行证据。由调用方决定是否抛出。

    Args:
        request: Invocation request with Flow identity, implementation identity, inputs, and context
                 包含 Flow 身份、实现身份、输入和上下文的调用请求
        provider: Provider that implements the business logic
                  实现业务逻辑的 Provider

    Returns:
        Tuple of (InvocationResult, ExecutionEvidence)
        (调用结果, 执行证据) 的元组
    """
    # Generate trace ID if not provided in context
    # 如果上下文中未提供，则生成追踪 ID
    trace_id = request.context.get("trace_id") or str(uuid.uuid4())
    invoked_by = request.context.get("invoked_by", "unknown")

    # Invoke the provider, capturing business failures as evidence
    # 调用 Provider，将业务失败捕获为证据
    try:
        result = provider.invoke(request)
    except Exception as exc:
        result = InvocationResult(
            flow_identity=request.flow_identity,
            implementation_identity=request.implementation_identity,
            outputs={},
            status="failure",
            error=f"{type(exc).__name__}: {exc}",
            execution_metadata={},
        )

    # Create execution evidence
    # 创建执行证据
    evidence = ExecutionEvidence.create(
        trace_id=trace_id,
        flow_identity=request.flow_identity,
        implementation_identity=request.implementation_identity,
        invocation_request=request,
        invocation_result=result,
        invoked_by=invoked_by,
    )

    return result, evidence


def create_invocation_request(
    flow_identity: FlowIdentity,
    implementation_identity: ImplementationIdentity,
    inputs: dict[str, Any],
    trace_id: str | None = None,
    invoked_by: str = "unknown"
) -> InvocationRequest:
    """Helper function to create an InvocationRequest.

    创建 InvocationRequest 的辅助函数。

    Args:
        flow_identity: Flow identity / Flow 身份
        implementation_identity: Implementation identity / 实现身份
        inputs: Typed inputs / 类型化输入
        trace_id: Optional trace ID (generated if not provided) / 可选的追踪 ID（未提供时生成）
        invoked_by: Who invoked the Flow ("host_cli" | "dagster") / 谁调用了 Flow

    Returns:
        InvocationRequest
        调用请求
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    return InvocationRequest(
        flow_identity=flow_identity,
        implementation_identity=implementation_identity,
        inputs=inputs,
        context={
            "trace_id": trace_id,
            "invoked_by": invoked_by
        }
    )
