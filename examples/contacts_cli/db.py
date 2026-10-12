"""
SQLite database operations for contact normalization.

This module handles reading from source database and writing to target database.
It is separate from the normalization logic to maintain separation of concerns.
"""

import sqlite3
from pathlib import Path
from typing import Any

from .normalize import normalize_contacts, NormalizationError


def read_contacts(db_path: str) -> list[dict[str, Any]]:
    """
    Read contacts from source SQLite database.

    Args:
        db_path: Path to source SQLite database

    Returns:
        List of contact dicts with keys: contact_id, full_name, email
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
    """
    Write normalized contacts to target SQLite database.

    This function creates the target table if it doesn't exist,
    and replaces all existing data (idempotent operation).

    Args:
        db_path: Path to target SQLite database
        contacts: List of normalized contact dicts
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


def process_contacts(source_db: str, target_db: str) -> dict[str, Any]:
    """
    Read, normalize, and write contacts.

    This function orchestrates the full pipeline:
    1. Read from source database
    2. Normalize contacts
    3. Write to target database

    If normalization fails, the target database is not modified.

    Args:
        source_db: Path to source SQLite database
        target_db: Path to target SQLite database

    Returns:
        Dict with processing results:
        - source_count: Number of contacts read
        - target_count: Number of contacts written
        - success: Boolean indicating success

    Raises:
        NormalizationError: If normalization fails (target not modified)
    """
    # Read contacts
    contacts = read_contacts(source_db)
    source_count = len(contacts)

    # Normalize contacts (may raise NormalizationError)
    normalized = normalize_contacts(contacts)
    target_count = len(normalized)

    # Write to target database
    write_contacts(target_db, normalized)

    return {
        "source_count": source_count,
        "target_count": target_count,
        "success": True,
    }
