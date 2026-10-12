"""CLI: Command-line interface entry point.

This is the trigger layer that receives external input, constructs execution requests,
and handles errors uniformly.
"""

import logging
import sys
from pathlib import Path

import typer

from contacts_cli.config import LOG_LEVEL
from contacts_cli.tasks import process_contacts_task

app = typer.Typer(help="Contact normalization CLI application")


def setup_logger() -> logging.Logger:
    """Create and configure logger."""
    logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s: %(message)s")
    return logging.getLogger(__name__)


@app.command()
def run(
    source: str = typer.Argument(..., help="Path to source SQLite database"),
    target: str = typer.Argument(..., help="Path to target SQLite database"),
) -> None:
    """Normalize contacts from source database to target database."""
    logger = setup_logger()

    # Validate source exists
    if not Path(source).exists():
        logger.error(f"Source database not found: {source}")
        raise typer.Exit(code=1)

    try:
        result = process_contacts_task(source, target, logger)
        logger.info(f"Successfully processed {result['target_count']} contacts")
    except Exception as e:
        logger.error(f"Failed to process contacts: {e}")
        raise typer.Exit(code=1)


@app.command()
def create_sample(
    output: str = typer.Argument("input.sqlite", help="Path to output SQLite database"),
) -> None:
    """Create a sample input database with test data."""
    import sqlite3

    logger = setup_logger()

    # Remove existing database if present
    if Path(output).exists():
        Path(output).unlink()

    conn = sqlite3.connect(output)

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

    logger.info(f"Created sample database: {output}")
    logger.info(f"Inserted {len(sample_data)} contacts")


if __name__ == "__main__":
    app()
