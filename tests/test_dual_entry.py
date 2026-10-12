"""P2 acceptance: dual-entry shared implementation.

Host CLI and Dagster must invoke the same business implementation through the
same Flow contract, record execution evidence, and not duplicate business
logic.

P2 验收：双入口共享实现。宿主 CLI 与 Dagster 必须通过同一 Flow 契约调用
同一业务实现，记录执行证据，且不重复业务逻辑。
"""

import hashlib
import logging
import sqlite3
import tempfile
from pathlib import Path

import pytest

from tinnery import FlowIdentity, create_invocation_request
from tinnery.dagster import FlowInvocationFailed, make_flow_job, make_flow_op

from contacts_cli import flows
from contacts_cli.flows import (
    FLOW_IDENTITY,
    IMPLEMENTATION_IDENTITY,
    ContactsNormalizeProvider,
    invoke_normalize_flow,
)
from contacts_cli.tasks import process_contacts_task
from contacts_cli.units import normalize as normalize_module

CONTACTS = [
    {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "},
    {"contact_id": 2, "full_name": "Bob  Smith", "email": "BOB@EXAMPLE.COM"},
]

EXPECTED_NORMALIZED = [
    {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
    {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
]


def _dagster_entry():
    """Execute the Dagster entry against the host-owned provider."""
    flow_op = make_flow_op(
        FLOW_IDENTITY, IMPLEMENTATION_IDENTITY, ContactsNormalizeProvider()
    )
    flow_job = make_flow_job(flow_op)
    execution = flow_job.execute_in_process(
        run_config={
            "ops": {flow_op.name: {"config": {"inputs": {"contacts": CONTACTS}}}}
        }
    )
    assert execution.success
    output = execution.output_for_node(flow_op.name)
    return flow_op, output["invocation_result"], output["execution_evidence"]


class TestSharedContractAcrossEntries:
    def test_both_entries_share_flow_identity(self):
        _, host_evidence = invoke_normalize_flow(CONTACTS, invoked_by="host_cli")
        _, _, dagster_evidence = _dagster_entry()

        assert host_evidence.flow_identity == FLOW_IDENTITY
        assert dagster_evidence.flow_identity == FLOW_IDENTITY
        assert host_evidence.flow_identity == dagster_evidence.flow_identity
        assert host_evidence.flow_identity.contract_version == "1.0.0"

    def test_both_entries_share_single_implementation_identity(self):
        _, host_evidence = invoke_normalize_flow(CONTACTS, invoked_by="host_cli")
        _, _, dagster_evidence = _dagster_entry()

        expected_hash = hashlib.sha256(
            Path(normalize_module.__file__).read_bytes()
        ).hexdigest()

        assert host_evidence.implementation_identity == IMPLEMENTATION_IDENTITY
        assert dagster_evidence.implementation_identity == IMPLEMENTATION_IDENTITY
        assert (
            host_evidence.implementation_identity.code_hash
            == dagster_evidence.implementation_identity.code_hash
            == expected_hash
        )

    def test_both_entries_produce_identical_business_output(self):
        host_result, _ = invoke_normalize_flow(CONTACTS, invoked_by="host_cli")
        _, dagster_result, _ = _dagster_entry()

        assert host_result.outputs == dagster_result.outputs
        assert host_result.outputs["normalized_contacts"] == EXPECTED_NORMALIZED
        assert dagster_result.outputs["normalized_contacts"] == EXPECTED_NORMALIZED

    def test_entries_are_distinguishable_and_evidence_verifiable(self):
        _, host_evidence = invoke_normalize_flow(CONTACTS, invoked_by="host_cli")
        _, _, dagster_evidence = _dagster_entry()

        assert host_evidence.invoked_by == "host_cli"
        assert dagster_evidence.invoked_by == "dagster"
        assert host_evidence.trace_id != dagster_evidence.trace_id
        assert dagster_evidence.trace_id.startswith("dagster:")

        assert host_evidence.verify_hash() is True
        assert dagster_evidence.verify_hash() is True


class TestSingleImplementationRouting:
    def test_both_entries_route_through_one_implementation(self, monkeypatch):
        calls = []
        real_normalize = flows.normalize_contacts

        def spy(contacts):
            calls.append(contacts)
            return real_normalize(contacts)

        monkeypatch.setattr(flows, "normalize_contacts", spy)

        # Host entry: the exact code path the CLI run command executes.
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"
            conn = sqlite3.connect(source_db)
            conn.execute(
                "CREATE TABLE raw_contacts "
                "(contact_id INTEGER PRIMARY KEY, full_name TEXT, email TEXT)"
            )
            conn.executemany(
                "INSERT INTO raw_contacts VALUES (?, ?, ?)",
                [(c["contact_id"], c["full_name"], c["email"]) for c in CONTACTS],
            )
            conn.commit()
            conn.close()

            task_result = process_contacts_task(
                str(source_db), str(target_db), logging.getLogger("test")
            )
            assert task_result["success"] is True

            conn = sqlite3.connect(target_db)
            rows = conn.execute(
                "SELECT contact_id, full_name, email FROM normalized_contacts"
            ).fetchall()
            conn.close()
            assert rows == [
                (1, "Alice Chen", "alice@example.com"),
                (2, "Bob Smith", "bob@example.com"),
            ]

        # Dagster entry against the same module-level function.
        _dagster_entry()

        # Both entries reached the single host-owned implementation.
        assert len(calls) == 2
        assert calls[0] == CONTACTS
        assert calls[1] == CONTACTS


class TestHostTaskEvidence:
    def test_task_records_execution_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"
            conn = sqlite3.connect(source_db)
            conn.execute(
                "CREATE TABLE raw_contacts "
                "(contact_id INTEGER PRIMARY KEY, full_name TEXT, email TEXT)"
            )
            conn.executemany(
                "INSERT INTO raw_contacts VALUES (?, ?, ?)",
                [(c["contact_id"], c["full_name"], c["email"]) for c in CONTACTS],
            )
            conn.commit()
            conn.close()

            result = process_contacts_task(
                str(source_db), str(target_db), logging.getLogger("test")
            )

        evidence = result["execution_evidence"]
        assert evidence.invoked_by == "host_cli"
        assert evidence.flow_identity == FLOW_IDENTITY
        assert evidence.implementation_identity == IMPLEMENTATION_IDENTITY
        assert evidence.verify_hash() is True
        assert result["trace_id"] == evidence.trace_id
        assert result["evidence_hash"] == evidence.evidence_hash

    def test_task_raises_and_skips_write_when_flow_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"
            conn = sqlite3.connect(source_db)
            conn.execute(
                "CREATE TABLE raw_contacts "
                "(contact_id INTEGER PRIMARY KEY, full_name TEXT, email TEXT)"
            )
            conn.execute(
                "INSERT INTO raw_contacts VALUES (1, NULL, 'alice@example.com')"
            )
            conn.commit()
            conn.close()

            with pytest.raises(RuntimeError, match="contacts.normalize flow failed"):
                process_contacts_task(
                    str(source_db), str(target_db), logging.getLogger("test")
                )

            assert not target_db.exists()


class TestDagsterOpContract:
    def test_op_name_derived_from_flow_id(self):
        flow_op = make_flow_op(
            FLOW_IDENTITY, IMPLEMENTATION_IDENTITY, ContactsNormalizeProvider()
        )
        assert flow_op.name == "contacts_normalize_flow_op"

    def test_failed_invocation_fails_dagster_step(self):
        class RejectingProvider:
            def invoke(self, request):
                raise ValueError("rejected by policy")

        flow_op = make_flow_op(FLOW_IDENTITY, IMPLEMENTATION_IDENTITY, RejectingProvider())
        flow_job = make_flow_job(flow_op)

        with pytest.raises(FlowInvocationFailed):
            flow_job.execute_in_process(
                run_config={"ops": {flow_op.name: {"config": {"inputs": {}}}}}
            )

    def test_provider_rejects_identity_mismatch(self):
        provider = ContactsNormalizeProvider()

        request = create_invocation_request(
            FLOW_IDENTITY, IMPLEMENTATION_IDENTITY, {"contacts": CONTACTS}
        )
        assert provider.invoke(request).is_success

        wrong_flow = FlowIdentity(
            flow_id="other.flow", version="1.0.0", contract_version="1.0.0"
        )
        wrong_request = create_invocation_request(
            wrong_flow, IMPLEMENTATION_IDENTITY, {"contacts": CONTACTS}
        )
        with pytest.raises(ValueError, match="Flow identity mismatch"):
            provider.invoke(wrong_request)
