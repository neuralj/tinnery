"""Invocation request and result definitions.

调用请求和结果定义。
"""

from dataclasses import dataclass
from typing import Any

from tinnery.identity import FlowIdentity, ImplementationIdentity


@dataclass(frozen=True)
class InvocationRequest:
    """Request to invoke a Flow.
    
    调用 Flow 的请求。
    """
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    inputs: dict[str, Any]    # Typed inputs / 类型化输入
    context: dict[str, Any]   # Execution context (trace_id, etc.) / 执行上下文
    
    def __str__(self) -> str:
        return f"InvocationRequest(flow={self.flow_identity}, impl={self.implementation_identity})"


@dataclass(frozen=True)
class InvocationResult:
    """Result of a Flow invocation.
    
    Flow 调用的结果。
    """
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    outputs: dict[str, Any]   # Typed outputs / 类型化输出
    status: str               # "success" | "failure" / 状态
    error: str | None         # Error message if failed / 失败时的错误消息
    execution_metadata: dict[str, Any]  # Duration, resource usage, etc. / 执行元数据
    
    def __str__(self) -> str:
        return f"InvocationResult(flow={self.flow_identity}, status={self.status})"
    
    @property
    def is_success(self) -> bool:
        """Check if invocation was successful.
        
        检查调用是否成功。
        """
        return self.status == "success"
