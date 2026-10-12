"""
Pure contact normalization logic.

This module contains only the transformation logic, independent of
database access or persistence. It receives records and returns
normalized records.
"""

from typing import Any


class NormalizationError(Exception):
    """Raised when contact normalization fails."""
    pass


def normalize_contact(contact: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a single contact record.

    Rules:
    - Preserve contact_id as the stable output key
    - Normalize full_name: trim whitespace, collapse consecutive spaces
    - Normalize email: trim whitespace, convert to lowercase
    - Reject null or empty normalized names
    - Reject null or empty normalized emails

    Args:
        contact: Input contact dict with keys: contact_id, full_name, email

    Returns:
        Normalized contact dict with same keys

    Raises:
        NormalizationError: If name or email is null/empty after normalization
    """
    # Extract fields
    contact_id = contact.get("contact_id")
    full_name = contact.get("full_name")
    email = contact.get("email")

    # Normalize full_name
    if full_name is None:
        raise NormalizationError(f"Contact {contact_id}: full_name is null")

    normalized_name = " ".join(str(full_name).split())

    if not normalized_name:
        raise NormalizationError(f"Contact {contact_id}: full_name is empty after normalization")

    # Normalize email
    if email is None:
        raise NormalizationError(f"Contact {contact_id}: email is null")

    normalized_email = str(email).strip().lower()

    if not normalized_email:
        raise NormalizationError(f"Contact {contact_id}: email is empty after normalization")

    return {
        "contact_id": contact_id,
        "full_name": normalized_name,
        "email": normalized_email,
    }


def normalize_contacts(contacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Normalize a batch of contacts.

    This function validates the complete input before returning any results.
    If any contact is invalid, the entire batch fails.

    Args:
        contacts: List of contact dicts

    Returns:
        List of normalized contact dicts

    Raises:
        NormalizationError: If any contact fails validation
    """
    normalized = []

    for contact in contacts:
        normalized_contact = normalize_contact(contact)
        normalized.append(normalized_contact)

    return normalized
