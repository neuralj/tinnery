"""Tests for Task layer."""

import logging
import sqlite3
import tempfile
from pathlib import Path

import pytest

from contacts_cli.tasks import process_contacts_task


class TestProcessContactsTask:
    """Tests for process_contacts_task."""

    def test_process_contacts_success(self):
        """Test successful processing of contacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"

            # Create source database with test data
            conn = sqlite3.connect(source_db)
            conn.execute("""
                CREATE TABLE raw_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    email TEXT
                )
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (1, '  Alice   Chen  ', ' ALICE@EXAMPLE.COM ')
            """)
            conn.commit()
            conn.close()

            # Create logger
            logger = logging.getLogger("test")

            # Process contacts
            result = process_contacts_task(str(source_db), str(target_db), logger)

            # Verify result
            assert result["success"] is True
            assert result["source_count"] == 1
            assert result["target_count"] == 1

            # Verify target database
            conn = sqlite3.connect(target_db)
            cursor = conn.execute("SELECT * FROM normalized_contacts")
            row = cursor.fetchone()
            conn.close()

            assert row == (1, "Alice Chen", "alice@example.com")

    def test_process_contacts_fails_on_invalid_input(self):
        """Test that processing fails on invalid input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"

            # Create source database with invalid data
            conn = sqlite3.connect(source_db)
            conn.execute("""
                CREATE TABLE raw_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    email TEXT
                )
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (1, NULL, 'alice@example.com')
            """)
            conn.commit()
            conn.close()

            # Create logger
            logger = logging.getLogger("test")

            # Process should fail
            with pytest.raises(Exception):
                process_contacts_task(str(source_db), str(target_db), logger)

            # Verify target database was not created
            assert not target_db.exists()
