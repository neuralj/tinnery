"""Flow: contacts.normalize — shared Tinnery contract for host CLI and Dagster.

This module defines the Flow identity, implementation identity, and typed
Provider for contact normalization. Both the host CLI (via its Task layer)
and Dagster invoke the same host-owned business implementation through this
single contract — the business logic lives only in units/normalize.py.

本模块定义联系人归一化 Flow 的身份、实现身份与类型化 Provider。宿主 CLI
（经其 Task 层）与 Dagster 都通过这同一契约调用宿主拥有的业务实现——业务
逻辑只存在于 units/normalize.py。
"""

import hashlib
import time
from pathlib import Path
from typing import Any, Callable

from tinnery import (
    FlowIdentity,
    ImplementationIdentity,
    InvocationResult,
    create_invocation_request,
    invoke_flow,
)

from contacts_cli.units import normalize as normalize_module
from contacts_cli.units.normalize import normalize_contacts

FLOW_IDENTITY = FlowIdentity(
    flow_id="contacts.normalize",
    version="1.0.0",
    contract_version="1.0.0",
)


def _implementation_identity() -> ImplementationIdentity:
    """Derive the implementation identity from the single business source file.

    从唯一的业务源文件派生实现身份。
    """
    source_path = Path(normalize_module.__file__)
    code_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    return ImplementationIdentity(
        implementation_id="contacts.normalize.host",
        version="1.0.0",
        code_hash=code_hash,
        metadata={
            "source": "contacts_cli/units/normalize.py",
            "entry": "normalize_contacts",
        },
    )


IMPLEMENTATION_IDENTITY = _implementation_identity()


class ContactsNormalizeProvider:
    """Typed Provider exposing the host-owned normalization implementation.

    暴露宿主拥有的归一化实现的类型化 Provider。

    Validates Flow and implementation identity before executing, so both
    entries can only reach this exact implementation.

    执行前校验 Flow 与实现身份，使两个入口只能到达这一份实现。
    """

    def __init__(
        self,
        implementation_identity: ImplementationIdentity = IMPLEMENTATION_IDENTITY,
        normalize_fn: Callable[[list[dict[str, Any]]], list[dict[str, Any]]] | None = None,
    ):
        self.implementation_identity = implementation_identity
        self._normalize_fn = normalize_fn or normalize_contacts

    def invoke(self, request) -> InvocationResult:
        if request.flow_identity != FLOW_IDENTITY:
            raise ValueError(
                f"Flow identity mismatch: expected {FLOW_IDENTITY}, "
                f"got {request.flow_identity}"
            )
        if request.implementation_identity != self.implementation_identity:
            raise ValueError(
                "Implementation identity mismatch: "
                f"expected {self.implementation_identity}, "
                f"got {request.implementation_identity}"
            )

        contacts = request.inputs["contacts"]

        started = time.perf_counter()
        normalized = self._normalize_fn(contacts)
        duration_ms = int((time.perf_counter() - started) * 1000)

        return InvocationResult(
            flow_identity=request.flow_identity,
            implementation_identity=self.implementation_identity,
            outputs={"normalized_contacts": normalized},
            status="success",
            error=None,
            execution_metadata={
                "duration_ms": duration_ms,
                "records_processed": len(contacts),
            },
        )


def invoke_normalize_flow(
    contacts: list[dict[str, Any]],
    trace_id: str | None = None,
    invoked_by: str = "host_cli",
) -> tuple[InvocationResult, Any]:
    """Invoke contacts.normalize through Tinnery Core.

    经由 Tinnery Core 调用 contacts.normalize。

    Returns (InvocationResult, ExecutionEvidence). Callers raise on failure.
    返回 (调用结果, 执行证据)。由调用方决定失败时是否抛出。
    """
    request = create_invocation_request(
        FLOW_IDENTITY,
        IMPLEMENTATION_IDENTITY,
        {"contacts": contacts},
        trace_id=trace_id,
        invoked_by=invoked_by,
    )
    return invoke_flow(request, ContactsNormalizeProvider())
