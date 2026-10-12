"""Unit: Database operations capability.

This unit provides a stable capability boundary for SQLite database operations.
It hides internal implementation details and exposes a clean input/output contract.
"""

import sqlite3
from typing import Any


def read_contacts(db_path: str) -> list[dict[str, Any]]:
    """Read contacts from source SQLite database.

    Contract:
        Input: path to source SQLite database
        Output: list of contact dicts with keys contact_id, full_name, email
        Errors: Raises sqlite3.Error on database failures
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute(
            "SELECT contact_id, full_name, email FROM raw_contacts"
        )

        contacts = []
        for row in cursor:
            contacts.append({
                "contact_id": row["contact_id"],
                "full_name": row["full_name"],
                "email": row["email"],
            })

        return contacts
    finally:
        conn.close()


def write_contacts(db_path: str, contacts: list[dict[str, Any]]) -> None:
    """Write normalized contacts to target SQLite database.

    Contract:
        Input: path to target SQLite database, list of normalized contact dicts
        Output: None (side effect: writes to database)
        Errors: Raises sqlite3.Error on database failures

    This function creates the target table if it doesn't exist,
    and replaces all existing data (idempotent operation).
    """
    conn = sqlite3.connect(db_path)

    try:
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS normalized_contacts (
                contact_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)

        # Clear existing data
        conn.execute("DELETE FROM normalized_contacts")

        # Insert normalized contacts
        conn.executemany(
            "INSERT INTO normalized_contacts (contact_id, full_name, email) VALUES (?, ?, ?)",
            [(c["contact_id"], c["full_name"], c["email"]) for c in contacts]
        )

        conn.commit()
    finally:
        conn.close()
