"""Flow: contacts.normalize — shared Tinnery contract for host CLI and Dagster.

This module defines the FlowContract and binds it to the host-owned
normalization function. Both the host CLI (via its Task layer) and Dagster
invoke the same host-owned business implementation through this single
contract — the business logic lives only in units/normalize.py.

本模块定义联系人归一化 FlowContract，并将其绑定到宿主拥有的归一化函数。
宿主 CLI（经其 Task 层）与 Dagster 都通过这同一契约调用宿主拥有的业务实现
——业务逻辑只存在于 units/normalize.py。
"""

from tinnery import FlowContract, bind_flow

from contacts_cli.units.normalize import normalize_contacts

CONTACT_SCHEMA_INPUT = {
    "type": "object",
    "properties": {
        "contact_id": {"type": "integer"},
        "full_name": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
    },
    "required": ["contact_id", "full_name", "email"],
    "additionalProperties": False,
}

CONTACT_SCHEMA_OUTPUT = {
    "type": "object",
    "properties": {
        "contact_id": {"type": "integer"},
        "full_name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "minLength": 1},
    },
    "required": ["contact_id", "full_name", "email"],
    "additionalProperties": False,
}

CONTACTS_CONTRACT = FlowContract.define(
    flow_id="contacts.normalize",
    contract_version="1.0.0",
    input_schema={"type": "array", "items": CONTACT_SCHEMA_INPUT},
    output_schema={"type": "array", "items": CONTACT_SCHEMA_OUTPUT},
    declared_effects=(),
)

# This binds the host-owned function, not a second implementation inside Tinnery.
CONTACTS_FLOW = bind_flow(CONTACTS_CONTRACT, normalize_contacts)
