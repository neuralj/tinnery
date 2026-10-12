"""
Unit tests for contact normalization logic.

These tests verify the pure transformation function, independent of database access.
"""

import unittest
from examples.contacts_cli.normalize import normalize_contact, normalize_contacts, NormalizationError


class TestNormalizeContact(unittest.TestCase):
    """Tests for single contact normalization."""

    def test_normalize_valid_contact(self):
        """Test normalization of a valid contact."""
        contact = {
            "contact_id": 1,
            "full_name": "  Alice   Chen  ",
            "email": " ALICE@EXAMPLE.COM "
        }

        result = normalize_contact(contact)

        self.assertEqual(result["contact_id"], 1)
        self.assertEqual(result["full_name"], "Alice Chen")
        self.assertEqual(result["email"], "alice@example.com")

    def test_normalize_collapses_whitespace(self):
        """Test that consecutive whitespace is collapsed to single space."""
        contact = {
            "contact_id": 2,
            "full_name": "Bob    Smith",
            "email": "bob@example.com"
        }

        result = normalize_contact(contact)

        self.assertEqual(result["full_name"], "Bob Smith")

    def test_normalize_trims_whitespace(self):
        """Test that leading/trailing whitespace is trimmed."""
        contact = {
            "contact_id": 3,
            "full_name": "  Charlie Brown  ",
            "email": "  CHARLIE@EXAMPLE.COM  "
        }

        result = normalize_contact(contact)

        self.assertEqual(result["full_name"], "Charlie Brown")
        self.assertEqual(result["email"], "charlie@example.com")

    def test_normalize_converts_email_to_lowercase(self):
        """Test that email is converted to lowercase."""
        contact = {
            "contact_id": 4,
            "full_name": "Diana Prince",
            "email": "DIANA@EXAMPLE.COM"
        }

        result = normalize_contact(contact)

        self.assertEqual(result["email"], "diana@example.com")

    def test_normalize_rejects_null_name(self):
        """Test that null name is rejected."""
        contact = {
            "contact_id": 5,
            "full_name": None,
            "email": "test@example.com"
        }

        with self.assertRaises(NormalizationError) as context:
            normalize_contact(contact)

        self.assertIn("full_name is null", str(context.exception))

    def test_normalize_rejects_empty_name(self):
        """Test that empty name after normalization is rejected."""
        contact = {
            "contact_id": 6,
            "full_name": "   ",
            "email": "test@example.com"
        }

        with self.assertRaises(NormalizationError) as context:
            normalize_contact(contact)

        self.assertIn("full_name is empty", str(context.exception))

    def test_normalize_rejects_null_email(self):
        """Test that null email is rejected."""
        contact = {
            "contact_id": 7,
            "full_name": "Eve Adams",
            "email": None
        }

        with self.assertRaises(NormalizationError) as context:
            normalize_contact(contact)

        self.assertIn("email is null", str(context.exception))

    def test_normalize_rejects_empty_email(self):
        """Test that empty email after normalization is rejected."""
        contact = {
            "contact_id": 8,
            "full_name": "Frank Miller",
            "email": "   "
        }

        with self.assertRaises(NormalizationError) as context:
            normalize_contact(contact)

        self.assertIn("email is empty", str(context.exception))

    def test_normalize_preserves_contact_id(self):
        """Test that contact_id is preserved unchanged."""
        contact = {
            "contact_id": 999,
            "full_name": "Grace Hopper",
            "email": "grace@example.com"
        }

        result = normalize_contact(contact)

        self.assertEqual(result["contact_id"], 999)


class TestNormalizeContacts(unittest.TestCase):
    """Tests for batch contact normalization."""

    def test_normalize_batch_valid_contacts(self):
        """Test normalization of a batch of valid contacts."""
        contacts = [
            {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "},
            {"contact_id": 2, "full_name": "Bob Smith", "email": "bob@example.com"},
        ]

        result = normalize_contacts(contacts)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["full_name"], "Alice Chen")
        self.assertEqual(result[0]["email"], "alice@example.com")
        self.assertEqual(result[1]["full_name"], "Bob Smith")
        self.assertEqual(result[1]["email"], "bob@example.com")

    def test_normalize_batch_fails_on_invalid_contact(self):
        """Test that batch fails if any contact is invalid."""
        contacts = [
            {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"},
            {"contact_id": 2, "full_name": None, "email": "bob@example.com"},  # Invalid
        ]

        with self.assertRaises(NormalizationError) as context:
            normalize_contacts(contacts)

        self.assertIn("Contact 2", str(context.exception))

    def test_normalize_batch_empty_list(self):
        """Test normalization of empty list."""
        result = normalize_contacts([])

        self.assertEqual(result, [])

    def test_normalize_batch_idempotent(self):
        """Test that normalizing the same input twice produces the same result."""
        contacts = [
            {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "},
        ]

        result1 = normalize_contacts(contacts)
        result2 = normalize_contacts(contacts)

        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()
