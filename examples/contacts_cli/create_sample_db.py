"""
Create a sample input database for testing.

Usage:
    python -m examples.contacts_cli.create_sample_db [output_path]

Default output: input.sqlite
"""

import sqlite3
import sys
from pathlib import Path


def create_sample_database(db_path: str = "input.sqlite"):
    """Create a sample input database with test data."""
    # Remove existing database if present
    if Path(db_path).exists():
        Path(db_path).unlink()

    conn = sqlite3.connect(db_path)

    # Create raw_contacts table
    conn.execute("""
        CREATE TABLE raw_contacts (
            contact_id INTEGER PRIMARY KEY,
            full_name TEXT,
            email TEXT
        )
    """)

    # Insert sample data with various normalization challenges
    sample_data = [
        (1, "  Alice   Chen  ", " ALICE@EXAMPLE.COM "),  # Whitespace and case
        (2, "Bob Smith", "BOB@EXAMPLE.COM"),  # Case only
        (3, "  Charlie Brown  ", "charlie@example.com"),  # Whitespace only
        (4, "Diana    Prince", "diana@example.com"),  # Multiple spaces
        (5, "Eve Adams", "EVE@EXAMPLE.COM"),  # Normal
    ]

    conn.executemany(
        "INSERT INTO raw_contacts (contact_id, full_name, email) VALUES (?, ?, ?)",
        sample_data
    )

    conn.commit()
    conn.close()

    print(f"Created sample database: {db_path}")
    print(f"Inserted {len(sample_data)} contacts")


if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "input.sqlite"
    create_sample_database(output_path)
