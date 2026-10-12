"""Versioned JSON-compatible Flow contracts with a deliberately small schema profile.

This is not a full JSON Schema implementation. Unsupported keywords fail closed.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping

JsonValue = Any
_SCHEMA_TYPES = {"object", "array", "string", "integer", "number", "boolean", "null"}


class ContractDefinitionError(ValueError):
    """The declared contract or schema is malformed or outside the v0.1 profile."""


class SchemaViolation(ValueError):
    """A value does not satisfy a Flow contract schema."""


def canonical_json(value: Any) -> str:
    """Serialize JSON data deterministically; NaN, infinity, and non-JSON values fail."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalise_type(value: Any, path: str) -> tuple[str, ...]:
    types = (value,) if isinstance(value, str) else tuple(value) if isinstance(value, list) else ()
    if not types or any(not isinstance(t, str) or t not in _SCHEMA_TYPES for t in types):
        raise ContractDefinitionError(f"{path}.type must name one or more supported JSON types")
    if len(set(types)) != len(types):
        raise ContractDefinitionError(f"{path}.type contains duplicates")
    return types


def _validate_schema_definition(schema: Any, path: str) -> None:
    if not isinstance(schema, dict):
        raise ContractDefinitionError(f"{path} must be an object")
    types = _normalise_type(schema.get("type"), path)
    allowed = {"type", "enum", "description"}
    if "object" in types:
        allowed |= {"properties", "required", "additionalProperties"}
    if "array" in types:
        allowed |= {"items", "minItems", "maxItems"}
    if "string" in types:
        allowed |= {"minLength", "maxLength"}
    if "integer" in types or "number" in types:
        allowed |= {"minimum", "maximum"}
    unsupported = set(schema) - allowed
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise ContractDefinitionError(f"{path} uses unsupported schema keywords: {names}")

    if "description" in schema and not isinstance(schema["description"], str):
        raise ContractDefinitionError(f"{path}.description must be a string")
    if "enum" in schema:
        if not isinstance(schema["enum"], list) or not schema["enum"]:
            raise ContractDefinitionError(f"{path}.enum must be a non-empty array")
        for item in schema["enum"]:
            try:
                canonical_json(item)
            except (TypeError, ValueError) as exc:
                raise ContractDefinitionError(f"{path}.enum must contain JSON values") from exc

    if "object" in types:
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)
        if not isinstance(properties, dict) or any(not isinstance(k, str) for k in properties):
            raise ContractDefinitionError(f"{path}.properties must be an object")
        if not isinstance(required, list) or any(not isinstance(k, str) for k in required):
            raise ContractDefinitionError(f"{path}.required must be an array of strings")
        if len(set(required)) != len(required) or not set(required).issubset(properties):
            raise ContractDefinitionError(f"{path}.required must be unique and declared in properties")
        if not isinstance(additional, bool):
            raise ContractDefinitionError(f"{path}.additionalProperties must be boolean")
        for key, child in properties.items():
            _validate_schema_definition(child, f"{path}.properties.{key}")

    if "array" in types:
        if "items" not in schema:
            raise ContractDefinitionError(f"{path}.items is required for array schemas")
        _validate_schema_definition(schema["items"], f"{path}.items")
        for key in ("minItems", "maxItems"):
            if key in schema and (not isinstance(schema[key], int) or isinstance(schema[key], bool) or schema[key] < 0):
                raise ContractDefinitionError(f"{path}.{key} must be a non-negative integer")
        if schema.get("minItems", 0) > schema.get("maxItems", math.inf):
            raise ContractDefinitionError(f"{path}.minItems cannot exceed maxItems")

    if "string" in types:
        for key in ("minLength", "maxLength"):
            if key in schema and (not isinstance(schema[key], int) or isinstance(schema[key], bool) or schema[key] < 0):
                raise ContractDefinitionError(f"{path}.{key} must be a non-negative integer")
        if schema.get("minLength", 0) > schema.get("maxLength", math.inf):
            raise ContractDefinitionError(f"{path}.minLength cannot exceed maxLength")

    if "integer" in types or "number" in types:
        for key in ("minimum", "maximum"):
            if key in schema and (not isinstance(schema[key], (int, float)) or isinstance(schema[key], bool) or not math.isfinite(schema[key])):
                raise ContractDefinitionError(f"{path}.{key} must be a finite number")
        if schema.get("minimum", -math.inf) > schema.get("maximum", math.inf):
            raise ContractDefinitionError(f"{path}.minimum cannot exceed maximum")


def validate_value(value: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    """Validate against the supported v0.1 schema subset, rejecting the first mismatch."""
    types = _normalise_type(schema.get("type"), path)

    def matches(kind: str) -> bool:
        if kind == "null": return value is None
        if kind == "boolean": return isinstance(value, bool)
        if kind == "integer": return isinstance(value, int) and not isinstance(value, bool)
        if kind == "number": return isinstance(value, (int, float)) and not isinstance(value, bool)
        if kind == "string": return isinstance(value, str)
        if kind == "array": return isinstance(value, list)
        if kind == "object": return isinstance(value, dict) and all(isinstance(k, str) for k in value)
        return False

    if not any(matches(kind) for kind in types):
        raise SchemaViolation(f"{path}: expected {' or '.join(types)}")
    if isinstance(value, float) and not math.isfinite(value):
        raise SchemaViolation(f"{path}: number must be finite")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaViolation(f"{path}: value is not an allowed enum member")

    if isinstance(value, dict) and "object" in types:
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                raise SchemaViolation(f"{path}.{key}: required field is missing")
        for key, item in value.items():
            if key in properties:
                validate_value(item, properties[key], f"{path}.{key}")
            elif schema.get("additionalProperties", True) is False:
                raise SchemaViolation(f"{path}.{key}: additional field is not allowed")

    if isinstance(value, list) and "array" in types:
        if len(value) < schema.get("minItems", 0):
            raise SchemaViolation(f"{path}: fewer items than minItems")
        if len(value) > schema.get("maxItems", math.inf):
            raise SchemaViolation(f"{path}: more items than maxItems")
        for index, item in enumerate(value):
            validate_value(item, schema["items"], f"{path}[{index}]")

    if isinstance(value, str) and "string" in types:
        if len(value) < schema.get("minLength", 0):
            raise SchemaViolation(f"{path}: string shorter than minLength")
        if len(value) > schema.get("maxLength", math.inf):
            raise SchemaViolation(f"{path}: string longer than maxLength")

    if isinstance(value, (int, float)) and not isinstance(value, bool) and ("integer" in types or "number" in types):
        if "minimum" in schema and value < schema["minimum"]:
            raise SchemaViolation(f"{path}: number below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise SchemaViolation(f"{path}: number above maximum")


@dataclass(frozen=True)
class FlowContract:
    """Immutable, versioned description of a Flow's JSON input/output boundary."""
    flow_id: str
    contract_version: str
    _input_schema_json: str
    _output_schema_json: str
    declared_effects: tuple[str, ...] = ()

    @classmethod
    def define(
        cls,
        flow_id: str,
        contract_version: str,
        input_schema: Mapping[str, Any],
        output_schema: Mapping[str, Any],
        declared_effects: tuple[str, ...] = (),
    ) -> "FlowContract":
        if not flow_id or any(ch.isspace() for ch in flow_id):
            raise ContractDefinitionError("flow_id must be non-empty and contain no whitespace")
        if not contract_version or any(ch.isspace() for ch in contract_version):
            raise ContractDefinitionError("contract_version must be non-empty and contain no whitespace")
        if any(not isinstance(effect, str) or not effect for effect in declared_effects):
            raise ContractDefinitionError("declared_effects must contain non-empty strings")
        _validate_schema_definition(dict(input_schema), "$input")
        _validate_schema_definition(dict(output_schema), "$output")
        try:
            input_text = canonical_json(dict(input_schema))
            output_text = canonical_json(dict(output_schema))
        except (TypeError, ValueError) as exc:
            raise ContractDefinitionError("contract schemas must be JSON data") from exc
        return cls(flow_id, contract_version, input_text, output_text, tuple(declared_effects))

    @property
    def input_schema(self) -> dict[str, Any]:
        return json.loads(self._input_schema_json)

    @property
    def output_schema(self) -> dict[str, Any]:
        return json.loads(self._output_schema_json)

    @property
    def digest(self) -> str:
        return sha256_text(canonical_json({
            "flow_id": self.flow_id,
            "contract_version": self.contract_version,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "declared_effects": list(self.declared_effects),
        }))

    def to_dict(self) -> dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "contract_version": self.contract_version,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "declared_effects": list(self.declared_effects),
            "contract_sha256": self.digest,
        }
