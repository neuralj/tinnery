"""Flow and Implementation identity definitions.

Flow 和实现身份定义。
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FlowIdentity:
    """Identity of a Flow.
    
    Flow 的身份标识。
    """
    flow_id: str              # Unique identifier / 唯一标识符
    version: str              # Flow version (semver) / Flow 版本（语义化版本）
    contract_version: str     # Contract version (semver) / 契约版本（语义化版本）
    
    def __str__(self) -> str:
        return f"{self.flow_id}@{self.version} (contract: {self.contract_version})"


@dataclass(frozen=True)
class ImplementationIdentity:
    """Identity of a business implementation.
    
    业务实现的身份标识。
    """
    implementation_id: str    # Unique identifier / 唯一标识符
    version: str              # Implementation version / 实现版本
    code_hash: str            # SHA256 hash of implementation code / 实现代码的 SHA256 哈希
    metadata: dict[str, Any]  # Additional metadata (author, timestamp, etc.) / 附加元数据
    
    def __str__(self) -> str:
        return f"{self.implementation_id}@{self.version} (hash: {self.code_hash[:16]}...)"
