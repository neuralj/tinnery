# contacts-cli

Contact normalization CLI application using CLI → Task → Unit architecture.

## Architecture

This application follows the three-layer architecture pattern:

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

### 1. Install dependencies

```bash
cd contacts_cli
uv venv
uv sync
```

### 2. Create sample database

```bash
uv run contacts-cli create-sample input.sqlite
```

### 3. Run normalization

```bash
uv run contacts-cli run input.sqlite output.sqlite
```

### 4. Verify output

```bash
python3 -c "import sqlite3; conn = sqlite3.connect('output.sqlite'); cursor = conn.execute('SELECT * FROM normalized_contacts ORDER BY contact_id'); [print(row) for row in cursor.fetchall()]; conn.close()"
```

## Run Tests

```bash
uv run pytest
```

## Dependencies

- Runtime: typer
- Dev: pytest
