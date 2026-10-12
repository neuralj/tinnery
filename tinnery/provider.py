"""Provider interface definition.

Provider 接口定义。
"""

from typing import Protocol

from tinnery.invocation import InvocationRequest, InvocationResult


class Provider(Protocol):
    """Abstract interface for business implementation providers.
    
    业务实现提供者的抽象接口。
    """
    
    def invoke(
        self,
        request: InvocationRequest
    ) -> InvocationResult:
        """Invoke the business implementation.
        
        调用业务实现。
        
        Args:
            request: Invocation request with Flow identity, implementation identity, inputs, and context
                     包含 Flow 身份、实现身份、输入和上下文的调用请求
        
        Returns:
            Invocation result with outputs, status, and execution metadata
            包含输出、状态和执行元数据的调用结果
        
        Raises:
            ValueError: If Flow identity or implementation identity does not match
                        如果 Flow 身份或实现身份不匹配
            Exception: If business logic fails
                       如果业务逻辑失败
        """
        ...
