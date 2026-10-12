"""Task: Contact normalization use case orchestrator.

This task orchestrates the complete use case of reading, normalizing, and writing contacts.
It coordinates multiple units to fulfill a single business requirement.
"""

import logging

from contacts_cli.units.database import read_contacts, write_contacts
from contacts_cli.units.normalize import normalize_contacts


def process_contacts_task(source: str, target: str, logger: logging.Logger) -> dict:
    """Orchestrate the contact normalization use case.

    Contract:
        Input: source database path, target database path, logger
        Output: dict with processing results
        Errors: Propagates exceptions from units

    This task:
        1. Reads contacts from source database
        2. Normalizes contacts using the normalization unit
        3. Writes normalized contacts to target database
        4. Returns processing statistics
    """
    logger.info("Reading contacts from source database")
    contacts = read_contacts(source)
    source_count = len(contacts)

    logger.info(f"Read {source_count} contacts")

    logger.info("Normalizing contacts")
    normalized = normalize_contacts(contacts)
    target_count = len(normalized)

    logger.info(f"Normalized {target_count} contacts")

    logger.info("Writing contacts to target database")
    write_contacts(target, normalized)

    logger.info(f"Wrote {target_count} contacts")

    return {
        "source_count": source_count,
        "target_count": target_count,
        "success": True,
    }
