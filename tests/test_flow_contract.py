"""Core protocol tests: FlowContract, bind_flow, Executor, ExecutionReceipt, verification.

核心协议测试：FlowContract、bind_flow、Executor、ExecutionReceipt、验证。
"""

import json
import tempfile
from pathlib import Path

import pytest

from tinnery import (
    ContractDefinitionError,
    EvidenceJournal,
    ExecutionReceipt,
    Executor,
    FlowContract,
    ImplementationIdentity,
    SchemaViolation,
    VerificationRecord,
    bind_flow,
    verify_output,
)


def identity_echo(payload):
    """Test implementation: returns payload as-is."""
    return payload


def broken_output(_payload):
    """Test implementation: returns invalid output."""
    return [{"contact_id": 1, "full_name": None, "email": "not-an-email"}]


def fails_at_runtime(_payload):
    """Test implementation: raises at runtime."""
    raise RuntimeError("sensitive details should not leak to receipt")


class TestFlowContract:
    def test_define_creates_contract_with_digest(self):
        contract = FlowContract.define(
            "demo.echo", "1.0", {"type": "object"}, {"type": "object"}
        )
        assert contract.flow_id == "demo.echo"
        assert contract.contract_version == "1.0"
        assert contract.digest

    def test_digest_is_key_order_independent(self):
        a = FlowContract.define(
            "demo.echo", "1.0",
            {"type": "object", "properties": {}, "required": []},
            {"type": "string"},
        )
        b = FlowContract.define(
            "demo.echo", "1.0",
            {"required": [], "properties": {}, "type": "object"},
            {"type": "string"},
        )
        assert a.digest == b.digest

    def test_fails_closed_on_unsupported_keyword(self):
        with pytest.raises(ContractDefinitionError, match="unsupported"):
            FlowContract.define(
                "demo.ref", "1",
                {"type": "object", "$ref": "#/definitions/x"},
                {"type": "object"},
            )

    def test_fails_on_empty_flow_id(self):
        with pytest.raises(ContractDefinitionError, match="flow_id"):
            FlowContract.define("", "1", {"type": "object"}, {"type": "object"})


class TestBindFlow:
    def test_bind_flow_creates_bound_flow_with_identity(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)
        assert bound.contract == contract
        assert bound.implementation == identity_echo
        assert isinstance(bound.identity, ImplementationIdentity)
        assert bound.identity.implementation_sha256

    def test_same_function_has_same_identity(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        first = bind_flow(contract, identity_echo)
        second = bind_flow(contract, identity_echo)
        assert first.identity.implementation_sha256 == second.identity.implementation_sha256
        assert first.identity.callable_code_sha256 == second.identity.callable_code_sha256


class TestExecutorSuccess:
    def test_successful_invocation(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)
        result = Executor().invoke(bound, {"x": 1})

        assert result.receipt.status == "SUCCEEDED"
        assert result.output == {"x": 1}
        assert result.receipt.input_sha256
        assert result.receipt.output_sha256
        assert result.receipt.contract_sha256 == contract.digest
        assert result.receipt.implementation_sha256 == bound.identity.implementation_sha256

    def test_receipt_has_runtime_info(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)
        result = Executor().invoke(bound, {})

        assert result.receipt.runtime["python_version"]
        assert result.receipt.runtime["platform"]
        assert result.receipt.execution_boundary == "trusted_in_process_no_sandbox"
        assert result.receipt.effects_enforced is False

    def test_journal_appends_receipt(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)

        with tempfile.TemporaryDirectory() as tmp:
            journal = EvidenceJournal(Path(tmp) / "evidence.jsonl")
            Executor(journal).invoke(bound, {"x": 1})

            lines = (Path(tmp) / "evidence.jsonl").read_text().splitlines()
            assert len(lines) == 1
            record = json.loads(lines[0])
            assert record["record_type"] == "execution_receipt"
            assert record["record"]["status"] == "SUCCEEDED"


class TestExecutorFailure:
    def test_input_contract_violation_rejects_before_execution(self):
        called = {"value": False}

        def should_not_run(payload):
            called["value"] = True
            return payload

        contract = FlowContract.define(
            "demo.id", "1",
            {"type": "object", "required": ["x"], "properties": {"x": {"type": "integer"}}},
            {"type": "object"},
        )
        bound = bind_flow(contract, should_not_run)
        result = Executor().invoke(bound, {"x": "not-an-integer"})

        assert result.receipt.status == "REJECTED"
        assert result.receipt.failure_code == "input_contract_violation"
        assert called["value"] is False

    def test_output_contract_violation_is_not_success(self):
        contract = FlowContract.define(
            "demo.bad-output", "1",
            {"type": "object"},
            {"type": "array", "items": {"type": "string"}},
        )
        bound = bind_flow(contract, broken_output)
        result = Executor().invoke(bound, {})

        assert result.receipt.status == "FAILED"
        assert result.receipt.failure_code == "output_contract_violation"
        assert result.output is None

    def test_implementation_exception_fails_without_leaking_message(self):
        contract = FlowContract.define("demo.error", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, fails_at_runtime)
        result = Executor().invoke(bound, {})

        assert result.receipt.status == "FAILED"
        assert result.receipt.failure_code == "implementation_exception"
        assert result.receipt.failure_type == "RuntimeError"
        assert "sensitive details" not in json.dumps(result.receipt.to_dict())


class TestVerification:
    def test_successful_execution_can_be_verified(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)
        result = Executor().invoke(bound, {"x": 1})

        def verifier(output):
            assert output == {"x": 1}
            return ("check_x",)

        record = verify_output(bound, result, "verifier-v1", verifier)
        assert record.status == "PASS"
        assert record.checks == ("check_x",)
        assert record.checked_output_sha256 == result.receipt.output_sha256

    def test_failed_execution_cannot_be_verified_as_pass(self):
        contract = FlowContract.define("demo.error", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, fails_at_runtime)
        result = Executor().invoke(bound, {})

        record = verify_output(bound, result, "verifier-v1", lambda o: ("check",))
        assert record.status == "SKIPPED"
        assert record.failure_code == "execution_not_succeeded"

    def test_implementation_cannot_self_certify(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)
        result = Executor().invoke(bound, {"x": 1})

        record = verify_output(bound, result, "same-function", bound.implementation)
        assert record.status == "REJECTED"
        assert record.failure_code == "self_verification_forbidden"

    def test_verification_appends_to_journal(self):
        contract = FlowContract.define("demo.echo", "1", {"type": "object"}, {"type": "object"})
        bound = bind_flow(contract, identity_echo)

        with tempfile.TemporaryDirectory() as tmp:
            journal = EvidenceJournal(Path(tmp) / "evidence.jsonl")
            result = Executor(journal).invoke(bound, {"x": 1})
            verify_output(bound, result, "v1", lambda o: ("check",), journal)

            lines = (Path(tmp) / "evidence.jsonl").read_text().splitlines()
            assert [json.loads(l)["record_type"] for l in lines] == [
                "execution_receipt", "verification_record"
            ]
