"""Task: Contact normalization use case orchestrator.

This task orchestrates the complete use case of reading, normalizing, and writing contacts.
The normalization step is invoked through Tinnery Core (the shared Flow contract),
so the host CLI and Dagster execute the same business implementation.
"""

import logging

from tinnery import Executor

from contacts_cli.flows import CONTACTS_FLOW
from contacts_cli.units.database import read_contacts, write_contacts


def process_contacts_task(source: str, target: str, logger: logging.Logger) -> dict:
    """Orchestrate the contact normalization use case.

    Contract:
        Input: source database path, target database path, logger
        Output: dict with processing results and execution receipt identifiers
        Errors: Raises if the Tinnery Flow invocation fails or units fail

    This task:
    1. Reads contacts from source database
    2. Normalizes contacts via Tinnery Core (contacts.normalize Flow)
    3. Writes normalized contacts to target database
    4. Returns processing statistics with execution receipt identifiers
    """
    logger.info("Reading contacts from source database")
    contacts = read_contacts(source)
    source_count = len(contacts)

    logger.info(f"Read {source_count} contacts")

    logger.info("Normalizing contacts through Tinnery Core")
    invocation = Executor().invoke(CONTACTS_FLOW, contacts)
    receipt = invocation.receipt
    if receipt.status != "SUCCEEDED":
        raise RuntimeError(
            f"contacts.normalize flow failed: {receipt.failure_code}"
        )
    normalized = invocation.output
    target_count = len(normalized)

    logger.info(
        "Normalized %d contacts (invocation=%s contract=%s impl=%s)",
        target_count,
        receipt.invocation_id,
        receipt.contract_sha256[:16],
        receipt.implementation_sha256[:16],
    )

    logger.info("Writing contacts to target database")
    write_contacts(target, normalized)

    logger.info(f"Wrote {target_count} contacts")

    return {
        "source_count": source_count,
        "target_count": target_count,
        "success": True,
        "invocation_id": receipt.invocation_id,
        "contract_sha256": receipt.contract_sha256,
        "implementation_sha256": receipt.implementation_sha256,
        "execution_receipt": receipt,
    }
