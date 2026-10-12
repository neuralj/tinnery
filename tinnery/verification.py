"""Independent verification records, deliberately separate from execution status."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

from .evidence import EvidenceJournal
from .identity import ImplementationIdentityError, identify
from .runtime import BoundFlow, InvocationResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class VerificationRecord:
    verification_version: str
    verification_id: str
    execution_invocation_id: str
    verified_at: str
    status: str
    verifier_id: str
    verifier_implementation_sha256: str | None
    verifier_source_sha256: str | None
    verifier_code_sha256: str | None
    checked_output_sha256: str | None
    checks: tuple[str, ...]
    failure_code: str | None
    failure_type: str | None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["checks"] = list(self.checks)
        return data


def verify_output(
    flow: BoundFlow,
    result: InvocationResult,
    verifier_id: str,
    verifier: Callable[[Any], Iterable[str]],
    journal: EvidenceJournal | None = None,
) -> VerificationRecord:
    """Run a separately identified verifier; a pass never changes execution status."""
    if not verifier_id or not verifier_id.strip():
        raise ValueError("verifier_id must be non-empty")

    status = "SKIPPED"
    failure_code = "execution_not_succeeded"
    failure_type: str | None = None
    checks: tuple[str, ...] = ()
    verifier_digest = source_digest = code_digest = None

    try:
        identity = identify(verifier)
        verifier_digest = identity.implementation_sha256
        source_digest = identity.module_source_sha256
        code_digest = identity.callable_code_sha256
    except ImplementationIdentityError:
        failure_code = "verifier_identity_unavailable"
        failure_type = "ImplementationIdentityError"

    if result.receipt.status == "SUCCEEDED" and verifier is flow.implementation:
        status = "REJECTED"
        failure_code = "self_verification_forbidden"
    elif result.receipt.status == "SUCCEEDED" and verifier_digest is not None:
        try:
            reported_checks = verifier(result.output)
            checks = tuple(reported_checks)
            if not checks or any(not isinstance(check, str) or not check.strip() for check in checks):
                raise ValueError("verifier must return one or more named successful checks")
        except Exception as exc:
            status = "FAIL"
            failure_code = "verification_failed"
            failure_type = type(exc).__name__
            checks = ()
        else:
            status = "PASS"
            failure_code = None
            failure_type = None

    record = VerificationRecord(
        verification_version="1",
        verification_id=__import__("uuid").uuid4().hex,
        execution_invocation_id=result.receipt.invocation_id,
        verified_at=_now(),
        status=status,
        verifier_id=verifier_id,
        verifier_implementation_sha256=verifier_digest,
        verifier_source_sha256=source_digest,
        verifier_code_sha256=code_digest,
        checked_output_sha256=result.receipt.output_sha256,
        checks=checks,
        failure_code=failure_code,
        failure_type=failure_type,
    )
    if journal is not None:
        journal.append_verification(record)
    return record
