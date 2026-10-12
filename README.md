# Tinnery

Tinnery is a shared Flow protocol and governance layer for CLI applications.

## Project Status

**Current Phase:** P1 — Host CLI Baseline (Completed)

The first demonstration validates a small, independently runnable SQLite contact-normalization CLI.

## Quick Start

### Run the Contact Normalization CLI

1. Create a sample input database:

```bash
python3 -m examples.contacts_cli.create_sample_db input.sqlite
```

2. Run the normalization CLI:

```bash
python3 -m examples.contacts_cli.cli input.sqlite output.sqlite
```

3. Verify the output:

```bash
python3 -c "import sqlite3; conn = sqlite3.connect('output.sqlite'); cursor = conn.execute('SELECT * FROM normalized_contacts ORDER BY contact_id'); [print(row) for row in cursor.fetchall()]; conn.close()"
```

### Run Tests

```bash
python3 -m unittest discover -s examples/contacts_cli/tests -v
```

## Documentation

- **Vision:** [`logos/VISION.md`](logos/VISION.md) — Long-term direction
- **Intent:** [`logos/intent.md`](logos/intent.md) — Current commitments
- **Current Slice:** [`current-slice.md`](current-slice.md) — Active task and authorization
- **Agent Instructions:** [`AGENTS.md`](AGENTS.md) — How to work with this repository

## Architecture

### P1: Host CLI Baseline

The contact normalization CLI demonstrates:

- **Pure transformation logic** (`examples/contacts_cli/normalize.py`): Independent of database access
- **Database operations** (`examples/contacts_cli/db.py`): SQLite read/write with separation of concerns
- **CLI interface** (`examples/contacts_cli/cli.py`): Command-line entry point
- **Comprehensive tests** (`examples/contacts_cli/tests/`): Unit and integration tests

### Transformation Contract

- Preserve `contact_id` as the stable output key
- Normalize `full_name`: trim whitespace, collapse consecutive spaces
- Normalize `email`: trim whitespace, convert to lowercase
- Reject null or empty normalized names/emails
- Validate complete input before mutating target (failure atomicity)

## Governance

This repository follows a structured governance model:

- **LOGOS** (`logos/`): Semantic authority (Vision, Intent, Decisions)
- **REALITY** (`reality/`): Observed facts with evidence
- **ENGINEERING** (`engineering/`): Proposed models and constraints
- **Current Slice** (`current-slice.md`): Active task authorization

See [`AGENTS.md`](AGENTS.md) for detailed governance rules.

## License

This is a demonstration project for the Tinnery Flow protocol.
