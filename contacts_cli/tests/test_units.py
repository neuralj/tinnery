"""Tests for Unit layer."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from contacts_cli.units.normalize import (
    normalize_contact,
    normalize_contacts,
    NormalizationError,
)
from contacts_cli.units.database import read_contacts, write_contacts


class TestNormalizeUnit:
    """Tests for normalization unit."""

    def test_normalize_valid_contact(self):
        """Test normalization of a valid contact."""
        contact = {
            "contact_id": 1,
            "full_name": "  Alice   Chen  ",
            "email": " ALICE@EXAMPLE.COM "
        }

        result = normalize_contact(contact)

        assert result["contact_id"] == 1
        assert result["full_name"] == "Alice Chen"
        assert result["email"] == "alice@example.com"

    def test_normalize_collapses_whitespace(self):
        """Test that consecutive whitespace is collapsed to single space."""
        contact = {
            "contact_id": 2,
            "full_name": "Bob    Smith",
            "email": "bob@example.com"
        }

        result = normalize_contact(contact)

        assert result["full_name"] == "Bob Smith"

    def test_normalize_rejects_null_name(self):
        """Test that null name is rejected."""
        contact = {
            "contact_id": 5,
            "full_name": None,
            "email": "test@example.com"
        }

        with pytest.raises(NormalizationError, match="full_name is null"):
            normalize_contact(contact)

    def test_normalize_rejects_empty_name(self):
        """Test that empty name after normalization is rejected."""
        contact = {
            "contact_id": 6,
            "full_name": "   ",
            "email": "test@example.com"
        }

        with pytest.raises(NormalizationError, match="full_name is empty"):
            normalize_contact(contact)

    def test_normalize_batch_valid_contacts(self):
        """Test normalization of a batch of valid contacts."""
        contacts = [
            {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "},
            {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
        ]

        result = normalize_contacts(contacts)

        assert len(result) == 2
        assert result[0]["full_name"] == "Alice Chen"
        assert result[0]["email"] == "alice@example.com"

    def test_normalize_batch_fails_on_invalid_contact(self):
        """Test that batch fails if any contact is invalid."""
        contacts = [
            {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
            {"contact_id": 2, "full_name": None, "email": "bob@example.com"},
        ]

        with pytest.raises(NormalizationError, match="Contact 2"):
            normalize_contacts(contacts)


class TestDatabaseUnit:
    """Tests for database unit."""

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
            conn.commit()
            conn.close()

            # Read contacts
            contacts = read_contacts(str(db_path))

            assert len(contacts) == 1
            assert contacts[0]["contact_id"] == 1
            assert contacts[0]["full_name"] == "Alice Chen"

    def test_write_contacts_to_target(self):
        """Test writing normalized contacts to target database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "target.sqlite"

            contacts = [
                {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
            ]

            # Write contacts
            write_contacts(str(db_path), contacts)

            # Verify written data
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT * FROM normalized_contacts")
            rows = cursor.fetchall()
            conn.close()

            assert len(rows) == 1
            assert rows[0] == (1, "Alice Chen", "alice@example.com")
