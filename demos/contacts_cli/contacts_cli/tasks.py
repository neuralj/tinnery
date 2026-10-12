"""Task: Contact normalization use case orchestrator.

This task orchestrates the complete use case of reading, normalizing, and writing contacts.
The normalization step is invoked through Tinnery Core (the shared Flow contract),
so the host CLI and Dagster execute the same business implementation.
"""

import logging

from contacts_cli.flows import invoke_normalize_flow
from contacts_cli.units.database import read_contacts, write_contacts


def process_contacts_task(source: str, target: str, logger: logging.Logger) -> dict:
    """Orchestrate the contact normalization use case.

    Contract:
        Input: source database path, target database path, logger
        Output: dict with processing results, Tinnery trace_id and evidence_hash
        Errors: Raises if the Tinnery Flow invocation fails or units fail

    This task:
    1. Reads contacts from source database
    2. Normalizes contacts via Tinnery Core (contacts.normalize Flow)
    3. Writes normalized contacts to target database
    4. Returns processing statistics with execution evidence identifiers
    """
    logger.info("Reading contacts from source database")
    contacts = read_contacts(source)
    source_count = len(contacts)

    logger.info(f"Read {source_count} contacts")

    logger.info("Normalizing contacts through Tinnery Core")
    result, evidence = invoke_normalize_flow(contacts, invoked_by="host_cli")
    if not result.is_success:
        raise RuntimeError(f"contacts.normalize flow failed: {result.error}")
    normalized = result.outputs["normalized_contacts"]
    target_count = len(normalized)

    logger.info(
        "Normalized %d contacts (trace_id=%s evidence_hash=%s)",
        target_count,
        evidence.trace_id,
        evidence.evidence_hash,
    )

    logger.info("Writing contacts to target database")
    write_contacts(target, normalized)

    logger.info(f"Wrote {target_count} contacts")

    return {
        "source_count": source_count,
        "target_count": target_count,
        "success": True,
        "trace_id": evidence.trace_id,
        "evidence_hash": evidence.evidence_hash,
        "invocation_result": result,
        "execution_evidence": evidence,
    }
