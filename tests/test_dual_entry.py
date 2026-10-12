"""P2 acceptance: dual-entry shared implementation.

Host CLI and Dagster must invoke the same business implementation through the
same Flow contract, record execution evidence, and not duplicate business
logic.

P2 验收：双入口共享实现。宿主 CLI 与 Dagster 必须通过同一 Flow 契约调用
同一业务实现，记录执行证据，且不重复业务逻辑。
"""

import logging
import sqlite3
import tempfile
from pathlib import Path

import pytest

from tinnery import Executor
from tinnery.dagster import FlowInvocationFailed, make_flow_job, make_flow_op

from contacts_cli import flows
from contacts_cli.flows import CONTACTS_CONTRACT, CONTACTS_FLOW
from contacts_cli.tasks import process_contacts_task

CONTACTS = [
    {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "},
    {"contact_id": 2, "full_name": "Bob  Smith", "email": "BOB@EXAMPLE.COM"},
]

EXPECTED_NORMALIZED = [
    {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
    {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
]


def _dagster_entry():
    """Execute the Dagster entry against the host-owned bound flow."""
    flow_op = make_flow_op(CONTACTS_FLOW)
    flow_job = make_flow_job(flow_op)
    execution = flow_job.execute_in_process(
        run_config={
            "ops": {flow_op.name: {"config": {"payload": CONTACTS}}}
        }
    )
    assert execution.success
    output = execution.output_for_node(flow_op.name)
    return flow_op, output["output"], output["receipt"]


class TestSharedContractAcrossEntries:
    def test_both_entries_share_contract_digest(self):
        host_invocation = Executor().invoke(CONTACTS_FLOW, CONTACTS)
        _, _, dagster_receipt = _dagster_entry()

        assert host_invocation.receipt.contract_sha256 == CONTACTS_CONTRACT.digest
        assert dagster_receipt.contract_sha256 == CONTACTS_CONTRACT.digest
        assert host_invocation.receipt.contract_sha256 == dagster_receipt.contract_sha256

    def test_both_entries_share_implementation_identity(self):
        host_invocation = Executor().invoke(CONTACTS_FLOW, CONTACTS)
        _, _, dagster_receipt = _dagster_entry()

        assert (
            host_invocation.receipt.implementation_sha256
            == CONTACTS_FLOW.identity.implementation_sha256
        )
        assert (
            dagster_receipt.implementation_sha256
            == CONTACTS_FLOW.identity.implementation_sha256
        )
        assert (
            host_invocation.receipt.module_source_sha256
            == dagster_receipt.module_source_sha256
        )
        assert (
            host_invocation.receipt.callable_code_sha256
            == dagster_receipt.callable_code_sha256
        )

    def test_both_entries_produce_identical_business_output(self):
        host_invocation = Executor().invoke(CONTACTS_FLOW, CONTACTS)
        _, dagster_output, _ = _dagster_entry()

        assert host_invocation.output == dagster_output
        assert host_invocation.output == EXPECTED_NORMALIZED
        assert dagster_output == EXPECTED_NORMALIZED

    def test_entries_are_distinguishable(self):
        host_invocation = Executor().invoke(CONTACTS_FLOW, CONTACTS)
        _, _, dagster_receipt = _dagster_entry()

        assert not host_invocation.receipt.invocation_id.startswith("dagster:")
        assert dagster_receipt.invocation_id.startswith("dagster:")
        assert host_invocation.receipt.invocation_id != dagster_receipt.invocation_id


class TestSingleImplementationRouting:
    def test_both_entries_use_same_bound_flow(self):
        """Both entries invoke the same BoundFlow object.

        两个入口调用同一个 BoundFlow 对象。
        """
        host_invocation = Executor().invoke(CONTACTS_FLOW, CONTACTS)
        _, _, dagster_receipt = _dagster_entry()

        # Both entries use the same BoundFlow (same contract + same implementation)
        assert host_invocation.receipt.implementation_sha256 == CONTACTS_FLOW.identity.implementation_sha256
        assert dagster_receipt.implementation_sha256 == CONTACTS_FLOW.identity.implementation_sha256
        assert host_invocation.receipt.contract_sha256 == CONTACTS_CONTRACT.digest
        assert dagster_receipt.contract_sha256 == CONTACTS_CONTRACT.digest

        # Both entries produce the same business output
        assert host_invocation.output == EXPECTED_NORMALIZED
        assert dagster_receipt.invocation_id.startswith("dagster:")


class TestHostTaskReceipt:
    def test_task_records_execution_receipt(self):
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

        receipt = result["execution_receipt"]
        assert receipt.status == "SUCCEEDED"
        assert receipt.contract_sha256 == CONTACTS_CONTRACT.digest
        assert receipt.implementation_sha256 == CONTACTS_FLOW.identity.implementation_sha256
        assert result["invocation_id"] == receipt.invocation_id
        assert result["contract_sha256"] == receipt.contract_sha256

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
        flow_op = make_flow_op(CONTACTS_FLOW)
        assert flow_op.name == "contacts_normalize_flow_op"

    def test_failed_invocation_fails_dagster_step(self):
        def rejecting_fn(payload):
            raise ValueError("rejected by policy")

        from tinnery import FlowContract, bind_flow

        contract = FlowContract.define(
            "demo.reject", "1", {"type": "object"}, {"type": "object"}
        )
        rejecting_flow = bind_flow(contract, rejecting_fn)

        flow_op = make_flow_op(rejecting_flow)
        flow_job = make_flow_job(flow_op)

        with pytest.raises(FlowInvocationFailed):
            flow_job.execute_in_process(
                run_config={"ops": {flow_op.name: {"config": {"payload": {}}}}}
            )

    def test_input_contract_violation_fails_dagster_step(self):
        flow_op = make_flow_op(CONTACTS_FLOW)
        flow_job = make_flow_job(flow_op)

        # contacts must be an array; providing a non-array triggers REJECTED
        with pytest.raises(FlowInvocationFailed):
            flow_job.execute_in_process(
                run_config={"ops": {flow_op.name: {"config": {"payload": "not-a-list"}}}}
            )
