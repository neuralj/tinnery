# Tinnery

Tinnery is a shared Flow protocol and governance layer for CLI applications.

## Project Status

**Current Phase:** P1 — Host CLI Baseline (Completed)

The first demonstration validates a small, independently runnable SQLite contact-normalization CLI using CLI → Task → Unit architecture.

## Architecture

The contacts-cli application follows the three-layer architecture pattern:

```
CLI (Trigger)
  ↓
Task (Orchestrator)
  ↓
Unit (Capability Boundary)
```

- **CLI Layer** (`cli.py`): Receives external input, constructs execution requests, handles errors uniformly
- **Task Layer** (`tasks.py`): Orchestrates the complete use case, coordinates multiple units
- **Unit Layer** (`units/`): Provides stable capability boundaries, hides internal implementation

## Quick Start

### Run the Contact Normalization CLI

1. Navigate to the contacts-cli directory:

```bash
cd demos/contacts_cli
```

2. Install dependencies:

```bash
uv venv
uv sync --extra dev
```

3. Create a sample input database:

```bash
uv run contacts-cli create-sample input.sqlite
```

4. Run the normalization CLI:

```bash
uv run contacts-cli run input.sqlite output.sqlite
```

5. Verify the output:

```bash
python3 -c "import sqlite3; conn = sqlite3.connect('output.sqlite'); cursor = conn.execute('SELECT * FROM normalized_contacts ORDER BY contact_id'); [print(row) for row in cursor.fetchall()]; conn.close()"
```

### Run Tests

```bash
cd demos/contacts_cli
uv run pytest -v
```

## Documentation

- **Vision:** [`logos/VISION.md`](logos/VISION.md) — Long-term direction
- **Intent:** [`logos/intent.md`](logos/intent.md) — Current commitments
- **Current Slice:** [`current-slice.md`](current-slice.md) — Active task and authorization
- **Agent Instructions:** [`AGENTS.md`](AGENTS.md) — How to work with this repository

## Governance

This repository follows a structured governance model:

- **LOGOS** (`logos/`): Semantic authority (Vision, Intent, Decisions)
- **REALITY** (`reality/`): Observed facts with evidence
- **ENGINEERING** (`engineering/`): Proposed models and constraints
- **Current Slice** (`current-slice.md`): Active task authorization

See [`AGENTS.md`](AGENTS.md) for detailed governance rules.

## License

This is a demonstration project for the Tinnery Flow protocol.
