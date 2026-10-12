"""In-process Flow invocation and execution receipts; no scheduler or plugin registry."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .contract import FlowContract, SchemaViolation, canonical_json, validate_value
from .evidence import EvidenceJournal
from .identity import ImplementationIdentity, ImplementationIdentityError, identify


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _digest_json(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BoundFlow:
    contract: FlowContract
    implementation: Callable[[Any], Any]
    identity: ImplementationIdentity
    dependency_manifest: Path | None = None


def bind_flow(
    contract: FlowContract,
    implementation: Callable[[Any], Any],
    dependency_manifest: str | Path | None = None,
) -> BoundFlow:
    manifest = Path(dependency_manifest).resolve() if dependency_manifest is not None else None
    identity = identify(implementation, manifest)
    return BoundFlow(contract, implementation, identity, manifest)


@dataclass(frozen=True)
class ExecutionReceipt:
    receipt_version: str
    invocation_id: str
    started_at: str
    finished_at: str
    status: str
    failure_code: str | None
    failure_type: str | None
    flow_id: str
    contract_version: str
    contract_sha256: str
    implementation_sha256: str
    entrypoint: str
    module_source_sha256: str
    callable_code_sha256: str
    dependency_manifest_sha256: str | None
    input_sha256: str | None
    output_sha256: str | None
    runtime: dict[str, str]
    execution_boundary: str
    declared_effects: tuple[str, ...]
    effects_enforced: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["declared_effects"] = list(self.declared_effects)
        return data


@dataclass(frozen=True)
class InvocationResult:
    output: Any
    receipt: ExecutionReceipt


class Executor:
    """Executes a bound trusted function and records outcome separately from verification."""
    def __init__(self, journal: EvidenceJournal | None = None):
        self.journal = journal

    def invoke(self, flow: BoundFlow, payload: Any, invocation_id: str | None = None) -> InvocationResult:
        started = _now()
        run_id = invocation_id or uuid.uuid4().hex
        input_digest: str | None = None
        output_digest: str | None = None
        output: Any = None
        status = "REJECTED"
        failure_code: str | None = None
        failure_type: str | None = None

        try:
            input_text = canonical_json(payload)
            input_digest = _digest_json(input_text)
            detached_payload = json.loads(input_text)
        except (TypeError, ValueError):
            detached_payload = None
            failure_code = "input_not_json"
            failure_type = "InputSerializationError"

        if failure_code is None:
            try:
                validate_value(detached_payload, flow.contract.input_schema)
            except SchemaViolation as exc:
                failure_code = "input_contract_violation"
                failure_type = type(exc).__name__

        if failure_code is None:
            try:
                current_identity = identify(flow.implementation, flow.dependency_manifest)
                if current_identity != flow.identity:
                    failure_code = "implementation_identity_drift"
                    failure_type = "ImplementationIdentityError"
            except ImplementationIdentityError as exc:
                failure_code = "implementation_identity_unavailable"
                failure_type = type(exc).__name__

        if failure_code is None:
            status = "FAILED"
            try:
                output = flow.implementation(detached_payload)
            except Exception as exc:
                failure_code = "implementation_exception"
                failure_type = type(exc).__name__
                output = None
            else:
                try:
                    output_text = canonical_json(output)
                    output_digest = _digest_json(output_text)
                    validate_value(json.loads(output_text), flow.contract.output_schema)
                except (TypeError, ValueError) as exc:
                    failure_code = "output_contract_violation"
                    failure_type = type(exc).__name__
                    output = None
                else:
                    status = "SUCCEEDED"
                    failure_code = None
                    failure_type = None

        identity = flow.identity
        receipt = ExecutionReceipt(
            receipt_version="1",
            invocation_id=run_id,
            started_at=started,
            finished_at=_now(),
            status=status,
            failure_code=failure_code,
            failure_type=failure_type,
            flow_id=flow.contract.flow_id,
            contract_version=flow.contract.contract_version,
            contract_sha256=flow.contract.digest,
            implementation_sha256=identity.implementation_sha256,
            entrypoint=identity.entrypoint,
            module_source_sha256=identity.module_source_sha256,
            callable_code_sha256=identity.callable_code_sha256,
            dependency_manifest_sha256=identity.dependency_manifest_sha256,
            input_sha256=input_digest,
            output_sha256=output_digest,
            runtime={
                "python_implementation": platform.python_implementation(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            execution_boundary="trusted_in_process_no_sandbox",
            declared_effects=flow.contract.declared_effects,
            effects_enforced=False,
        )
        if self.journal is not None:
            self.journal.append_execution(receipt)
        return InvocationResult(output=output if status == "SUCCEEDED" else None, receipt=receipt)
