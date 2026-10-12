"""Execution evidence definition.

执行证据定义。
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from tinnery.identity import FlowIdentity, ImplementationIdentity
from tinnery.invocation import InvocationRequest, InvocationResult


@dataclass(frozen=True)
class ExecutionEvidence:
    """Evidence of a Flow execution.
    
    Flow 执行的证据。
    """
    trace_id: str                          # Unique trace identifier / 唯一追踪标识符
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    invocation_request: InvocationRequest
    invocation_result: InvocationResult
    invoked_by: str                        # "host_cli" | "dagster" / 调用方
    timestamp: str                         # ISO 8601 / ISO 8601 时间戳
    evidence_hash: str                     # SHA256 hash of evidence / 证据的 SHA256 哈希
    
    def __str__(self) -> str:
        return f"ExecutionEvidence(trace={self.trace_id}, flow={self.flow_identity}, invoked_by={self.invoked_by})"
    
    @staticmethod
    def create(
        trace_id: str,
        flow_identity: FlowIdentity,
        implementation_identity: ImplementationIdentity,
        invocation_request: InvocationRequest,
        invocation_result: InvocationResult,
        invoked_by: str
    ) -> "ExecutionEvidence":
        """Create execution evidence with computed hash.
        
        创建带有计算哈希的执行证据。
        
        Args:
            trace_id: Unique trace identifier / 唯一追踪标识符
            flow_identity: Flow identity / Flow 身份
            implementation_identity: Implementation identity / 实现身份
            invocation_request: Invocation request / 调用请求
            invocation_result: Invocation result / 调用结果
            invoked_by: Who invoked the Flow ("host_cli" | "dagster") / 谁调用了 Flow
        
        Returns:
            ExecutionEvidence with computed hash
            带有计算哈希的执行证据
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Compute evidence hash
        # 计算证据哈希
        evidence_data = {
            "trace_id": trace_id,
            "flow_identity": {
                "flow_id": flow_identity.flow_id,
                "version": flow_identity.version,
                "contract_version": flow_identity.contract_version
            },
            "implementation_identity": {
                "implementation_id": implementation_identity.implementation_id,
                "version": implementation_identity.version,
                "code_hash": implementation_identity.code_hash
            },
            "invoked_by": invoked_by,
            "timestamp": timestamp,
            "request_inputs": invocation_request.inputs,
            "result_status": invocation_result.status,
            "result_outputs": invocation_result.outputs
        }
        
        evidence_json = json.dumps(evidence_data, sort_keys=True)
        evidence_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        return ExecutionEvidence(
            trace_id=trace_id,
            flow_identity=flow_identity,
            implementation_identity=implementation_identity,
            invocation_request=invocation_request,
            invocation_result=invocation_result,
            invoked_by=invoked_by,
            timestamp=timestamp,
            evidence_hash=evidence_hash
        )
    
    def verify_hash(self) -> bool:
        """Verify the evidence hash is correct.
        
        验证证据哈希是否正确。
        
        Returns:
            True if hash is valid, False otherwise
            如果哈希有效返回 True，否则返回 False
        """
        evidence_data = {
            "trace_id": self.trace_id,
            "flow_identity": {
                "flow_id": self.flow_identity.flow_id,
                "version": self.flow_identity.version,
                "contract_version": self.flow_identity.contract_version
            },
            "implementation_identity": {
                "implementation_id": self.implementation_identity.implementation_id,
                "version": self.implementation_identity.version,
                "code_hash": self.implementation_identity.code_hash
            },
            "invoked_by": self.invoked_by,
            "timestamp": self.timestamp,
            "request_inputs": self.invocation_request.inputs,
            "result_status": self.invocation_result.status,
            "result_outputs": self.invocation_result.outputs
        }
        
        evidence_json = json.dumps(evidence_data, sort_keys=True)
        computed_hash = hashlib.sha256(evidence_json.encode()).hexdigest()
        
        return computed_hash == self.evidence_hash
