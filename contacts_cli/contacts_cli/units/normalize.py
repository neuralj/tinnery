"""Unit: Contact normalization capability.

This unit provides a stable capability boundary for normalizing contact records.
It hides internal implementation details and exposes a clean input/output contract.
"""

from typing import Any


class NormalizationError(Exception):
    """Raised when contact normalization fails."""
    pass


def normalize_contact(contact: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single contact record.

    Contract:
        Input: dict with keys contact_id, full_name, email
        Output: dict with same keys, normalized values
        Errors: Raises NormalizationError if validation fails

    Rules:
        - Preserve contact_id as the stable output key
        - Normalize full_name: trim whitespace, collapse consecutive spaces
        - Normalize email: trim whitespace, convert to lowercase
        - Reject null or empty normalized names
        - Reject null or empty normalized emails
    """
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
    """Normalize a batch of contacts.

    Contract:
        Input: list of contact dicts
        Output: list of normalized contact dicts
        Errors: Raises NormalizationError if any contact fails validation

    This function validates the complete input before returning any results.
    If any contact is invalid, the entire batch fails.
    """
    normalized = []

    for contact in contacts:
        normalized_contact = normalize_contact(contact)
        normalized.append(normalized_contact)

    return normalized
