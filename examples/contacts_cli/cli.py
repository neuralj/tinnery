"""
Command-line interface for contact normalization.

Usage:
    python -m examples.contacts_cli.cli <source_db> <target_db>

Example:
    python -m examples.contacts_cli.cli input.sqlite output.sqlite
"""

import sys
from pathlib import Path

from .db import process_contacts
from .normalize import NormalizationError


def main():
    """Main entry point for the CLI."""
    if len(sys.argv) != 3:
        print("Usage: python -m examples.contacts_cli.cli <source_db> <target_db>")
        print("Example: python -m examples.contacts_cli.cli input.sqlite output.sqlite")
        sys.exit(1)

    source_db = sys.argv[1]
    target_db = sys.argv[2]

    # Validate paths
    if not Path(source_db).exists():
        print(f"Error: Source database not found: {source_db}")
        sys.exit(1)

    try:
        result = process_contacts(source_db, target_db)
        print(f"Success: Processed {result['source_count']} contacts")
        print(f"  Source: {source_db}")
        print(f"  Target: {target_db}")
        print(f"  Written: {result['target_count']} contacts")
    except NormalizationError as e:
        print(f"Error: Normalization failed: {e}")
        print("Target database was not modified.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
