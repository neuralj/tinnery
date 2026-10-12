"""
Integration tests for contact normalization pipeline.

These tests verify the full pipeline including database operations.
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from examples.contacts_cli.db import read_contacts, write_contacts, process_contacts
from examples.contacts_cli.normalize import NormalizationError


class TestDatabaseOperations(unittest.TestCase):
    """Tests for database read/write operations."""

    def test_read_contacts_from_source(self):
        """Test reading contacts from source database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "source.sqlite"

            # Create source database with test data
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE raw_contacts (
                    contact_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    email TEXT
                )
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (1, 'Alice Chen', 'alice@example.com')
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (2, 'Bob Smith', 'bob@example.com')
            """)
            conn.commit()
            conn.close()

            # Read contacts
            contacts = read_contacts(str(db_path))

            self.assertEqual(len(contacts), 2)
            self.assertEqual(contacts[0]["contact_id"], 1)
            self.assertEqual(contacts[0]["full_name"], "Alice Chen")
            self.assertEqual(contacts[0]["email"], "alice@example.com")

    def test_write_contacts_to_target(self):
        """Test writing normalized contacts to target database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "target.sqlite"

            contacts = [
                {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
                {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
            ]

            # Write contacts
            write_contacts(str(db_path), contacts)

            # Verify written data
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT * FROM normalized_contacts ORDER BY contact_id")
            rows = cursor.fetchall()
            conn.close()

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], (1, "Alice Chen", "alice@example.com"))
            self.assertEqual(rows[1], (2, "Bob Smith", "bob@example.com"))

    def test_write_contacts_replaces_existing_data(self):
        """Test that writing contacts replaces existing data (idempotent)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "target.sqlite"

            # Write initial data
            contacts1 = [
                {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
            ]
            write_contacts(str(db_path), contacts1)

            # Write new data
            contacts2 = [
                {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
            ]
            write_contacts(str(db_path), contacts2)

            # Verify only new data exists
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT * FROM normalized_contacts")
            rows = cursor.fetchall()
            conn.close()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0], (2, "Bob Smith", "bob@example.com"))


class TestProcessContacts(unittest.TestCase):
    """Tests for the full processing pipeline."""

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

            # Process contacts
            result = process_contacts(str(source_db), str(target_db))

            # Verify result
            self.assertTrue(result["success"])
            self.assertEqual(result["source_count"], 1)
            self.assertEqual(result["target_count"], 1)

            # Verify target database
            conn = sqlite3.connect(target_db)
            cursor = conn.execute("SELECT * FROM normalized_contacts")
            row = cursor.fetchone()
            conn.close()

            self.assertEqual(row, (1, "Alice Chen", "alice@example.com"))

    def test_process_contacts_fails_on_invalid_input(self):
        """Test that processing fails on invalid input without modifying target."""
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

            # Process should fail
            with self.assertRaises(NormalizationError):
                process_contacts(str(source_db), str(target_db))

            # Verify target database was not created or modified
            self.assertFalse(target_db.exists())

    def test_process_contacts_idempotent(self):
        """Test that processing the same input twice produces the same result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"

            # Create source database
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
                VALUES (1, 'Alice Chen', 'alice@example.com')
            """)
            conn.commit()
            conn.close()

            # Process twice
            result1 = process_contacts(str(source_db), str(target_db))
            result2 = process_contacts(str(source_db), str(target_db))

            # Verify same result
            self.assertEqual(result1, result2)

    def test_process_contacts_failure_atomicity(self):
        """Test that failed processing doesn't leave partial results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_db = Path(tmpdir) / "source.sqlite"
            target_db = Path(tmpdir) / "target.sqlite"

            # Create source database with mixed valid/invalid data
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
                VALUES (1, 'Alice Chen', 'alice@example.com')
            """)
            conn.execute("""
                INSERT INTO raw_contacts (contact_id, full_name, email)
                VALUES (2, NULL, 'bob@example.com')
            """)
            conn.commit()
            conn.close()

            # Process should fail
            with self.assertRaises(NormalizationError):
                process_contacts(str(source_db), str(target_db))

            # Verify target database doesn't exist (no partial results)
            self.assertFalse(target_db.exists())


if __name__ == "__main__":
    unittest.main()
