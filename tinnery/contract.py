"""Flow contract definition.

Flow 契约定义。
"""

from dataclasses import dataclass, field
from typing import Any

from tinnery.identity import FlowIdentity


@dataclass(frozen=True)
class FlowContract:
    """Contract for a Flow.
    
    Flow 的契约定义。
    """
    flow_identity: FlowIdentity
    input_schema: dict[str, Any]        # JSON Schema or type definition / JSON Schema 或类型定义
    output_schema: dict[str, Any]       # JSON Schema or type definition / JSON Schema 或类型定义
    side_effects: list[str] = field(default_factory=list)  # Declared side effects / 声明的副作用
    
    def __str__(self) -> str:
        return f"FlowContract(flow={self.flow_identity}, side_effects={self.side_effects})"
    
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs against input schema.
        
        根据输入 schema 验证输入。
        
        Note: This is a simplified validation. In production, use jsonschema or similar.
        注意：这是简化的验证。在生产环境中，使用 jsonschema 或类似工具。
        """
        # Simplified validation: check required fields
        # 简化验证：检查必需字段
        required = self.input_schema.get("required", [])
        for field_name in required:
            if field_name not in inputs:
                raise ValueError(f"Missing required input field: {field_name}")
        return True
    
    def validate_outputs(self, outputs: dict[str, Any]) -> bool:
        """Validate outputs against output schema.
        
        根据输出 schema 验证输出。
        
        Note: This is a simplified validation. In production, use jsonschema or similar.
        注意：这是简化的验证。在生产环境中，使用 jsonschema 或类似工具。
        """
        # Simplified validation: check required fields
        # 简化验证：检查必需字段
        required = self.output_schema.get("required", [])
        for field_name in required:
            if field_name not in outputs:
                raise ValueError(f"Missing required output field: {field_name}")
        return True
