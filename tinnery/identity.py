"""Source-level and loaded-code identity for plain Python functions."""
from __future__ import annotations

import dis
import hashlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from types import FunctionType

from .contract import canonical_json


class ImplementationIdentityError(RuntimeError):
    """Implementation identity cannot be established reliably."""


@dataclass(frozen=True)
class ImplementationIdentity:
    entrypoint: str
    module_source_sha256: str
    callable_code_sha256: str
    dependency_manifest_sha256: str | None
    implementation_sha256: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "entrypoint": self.entrypoint,
            "module_source_sha256": self.module_source_sha256,
            "callable_code_sha256": self.callable_code_sha256,
            "dependency_manifest_sha256": self.dependency_manifest_sha256,
            "implementation_sha256": self.implementation_sha256,
        }


def identify(function: FunctionType, dependency_manifest: Path | None = None) -> ImplementationIdentity:
    """Hash the defining source file, callable's disassembly, and optional lock/manifest.

    Paths are deliberately not included in the digest so identical checked-out source can
    have the same source identity from different absolute directories. This remains a
    source-level identity, not proof of all transitive runtime dependencies.
    """
    if not inspect.isfunction(function):
        raise ImplementationIdentityError("v0.1 supports plain Python functions only")
    source_path = inspect.getsourcefile(function)
    if not source_path:
        raise ImplementationIdentityError("function source file cannot be located")
    source_file = Path(source_path).resolve()
    if not source_file.is_file():
        raise ImplementationIdentityError("function source file is not available")
    try:
        source_digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
        code_digest = hashlib.sha256(dis.Bytecode(function).dis().encode("utf-8")).hexdigest()
        dependency_digest = None
        if dependency_manifest is not None:
            manifest = Path(dependency_manifest).resolve()
            if not manifest.is_file():
                raise ImplementationIdentityError("dependency manifest is not available")
            dependency_digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    except OSError as exc:
        raise ImplementationIdentityError("implementation identity inputs could not be read") from exc

    entrypoint = f"{function.__module__}:{function.__qualname__}"
    source_identity = {
        "entrypoint": entrypoint,
        "module_source_sha256": source_digest,
        "dependency_manifest_sha256": dependency_digest,
    }
    implementation_digest = hashlib.sha256(canonical_json(source_identity).encode("utf-8")).hexdigest()
    return ImplementationIdentity(
        entrypoint=entrypoint,
        module_source_sha256=source_digest,
        callable_code_sha256=code_digest,
        dependency_manifest_sha256=dependency_digest,
        implementation_sha256=implementation_digest,
    )
