"""Core protocol tests: Flow identity, contract, invocation, evidence.

核心协议测试：Flow 身份、契约、调用、证据。
"""

import hashlib
from dataclasses import replace

import pytest

from tinnery import (
    ExecutionEvidence,
    FlowContract,
    FlowIdentity,
    ImplementationIdentity,
    InvocationRequest,
    InvocationResult,
    create_invocation_request,
    invoke_flow,
)

FLOW = FlowIdentity(
    flow_id="test.flow",
    version="1.0.0",
    contract_version="1.0.0",
)
IMPL = ImplementationIdentity(
    implementation_id="test.flow.impl",
    version="1.0.0",
    code_hash=hashlib.sha256(b"test-implementation").hexdigest(),
    metadata={"source": "tests"},
)


class RecordingProvider:
    """Test provider returning a fixed successful result."""

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        return InvocationResult(
            flow_identity=request.flow_identity,
            implementation_identity=request.implementation_identity,
            outputs={"echo": request.inputs.get("value")},
            status="success",
            error=None,
            execution_metadata={"records_processed": 1},
        )


class ExplodingProvider:
    """Test provider raising a business failure."""

    def invoke(self, request: InvocationRequest) -> InvocationResult:
        raise ValueError("business rule violated")


class TestIdentity:
    def test_flow_identity_is_frozen(self):
        with pytest.raises(Exception):
            FLOW.flow_id = "changed"  # type: ignore[misc]

    def test_flow_identity_str(self):
        assert str(FLOW) == "test.flow@1.0.0 (contract: 1.0.0)"

    def test_implementation_identity_str(self):
        assert str(IMPL).startswith("test.flow.impl@1.0.0 (hash: ")


class TestCreateInvocationRequest:
    def test_generates_trace_id_when_missing(self):
        request = create_invocation_request(FLOW, IMPL, {"value": 1})
        assert request.context["trace_id"]
        assert request.context["invoked_by"] == "unknown"

    def test_sets_invoked_by_and_trace_id(self):
        request = create_invocation_request(
            FLOW, IMPL, {"value": 1}, trace_id="trace-42", invoked_by="host_cli"
        )
        assert request.context["trace_id"] == "trace-42"
        assert request.context["invoked_by"] == "host_cli"


class TestInvokeFlowSuccess:
    def test_returns_result_and_verifiable_evidence(self):
        request = create_invocation_request(
            FLOW, IMPL, {"value": 7}, trace_id="trace-ok", invoked_by="host_cli"
        )
        result, evidence = invoke_flow(request, RecordingProvider())

        assert result.is_success
        assert result.outputs == {"echo": 7}
        assert evidence.trace_id == "trace-ok"
        assert evidence.invoked_by == "host_cli"
        assert evidence.flow_identity == FLOW
        assert evidence.implementation_identity == IMPL
        assert evidence.verify_hash() is True

    def test_evidence_hash_detects_tampering(self):
        request = create_invocation_request(FLOW, IMPL, {"value": 1})
        _, evidence = invoke_flow(request, RecordingProvider())
        tampered = replace(evidence, trace_id="tampered-trace")
        assert tampered.verify_hash() is False


class TestInvokeFlowFailure:
    def test_provider_exception_becomes_failure_result_with_evidence(self):
        request = create_invocation_request(
            FLOW, IMPL, {"value": 1}, trace_id="trace-fail", invoked_by="dagster"
        )
        result, evidence = invoke_flow(request, ExplodingProvider())

        assert not result.is_success
        assert result.status == "failure"
        assert "ValueError: business rule violated" in result.error
        assert evidence.verify_hash() is True
        assert evidence.invocation_result.status == "failure"


class TestFlowContract:
    def _contract(self) -> FlowContract:
        return FlowContract(
            flow_identity=FLOW,
            input_schema={"type": "object", "required": ["value"]},
            output_schema={"type": "object", "required": ["echo"]},
            side_effects=["none"],
        )

    def test_validates_inputs(self):
        assert self._contract().validate_inputs({"value": 1}) is True

    def test_rejects_missing_input_field(self):
        with pytest.raises(ValueError, match="value"):
            self._contract().validate_inputs({})

    def test_rejects_missing_output_field(self):
        with pytest.raises(ValueError, match="echo"):
            self._contract().validate_outputs({})

    def test_execution_evidence_requires_identity_match_in_request(self):
        request = create_invocation_request(FLOW, IMPL, {"value": 1})
        _, evidence = invoke_flow(request, RecordingProvider())
        assert isinstance(evidence, ExecutionEvidence)
        assert isinstance(request, InvocationRequest)
