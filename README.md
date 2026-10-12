# Tinnery

Tinnery is a shared Flow protocol and governance layer for CLI applications.

## Project Status

**Current Phase:** P2 — Shared Flow Protocol (Active)

- **P1 — Host CLI Baseline:** Completed. A contacts-normalization CLI using CLI → Task → Unit architecture.
- **P2 — Shared Flow Protocol:** Tinnery Core library and Dagster integration proving that a host CLI and Dagster invoke the same business implementation through one versioned Flow contract, with execution evidence on both entries.
- **P3 — Version Governance:** Not yet authorized.

## Architecture

### Dual-Entry Flow Invocation (P2)

```
Host CLI ──► Task ──► Tinnery Core ◄── Dagster Op/Job
                          │
                          ▼
              Typed Provider (host-owned)
                          │
                          ▼
              Business implementation (single source)
```

- **Tinnery Core** (`tinnery/`): Flow identity, typed invocation protocol, execution evidence. Independent of Dagster.
- **Dagster Integration** (`tinnery/dagster/`): Maps Dagster run requests (op config) to Tinnery Flow invocations.
- **Host demo** (`demos/contacts_cli/`): Runs without Dagster; its Task layer invokes the Flow through Tinnery Core.
- **Flow contract spec:** [`engineering/flow-contract.md`](engineering/flow-contract.md)

### Three-Layer Host Architecture (P1)

```
CLI (Trigger) → Task (Orchestrator) → Unit (Capability Boundary)
```

## Quick Start

### Run the Contact Normalization CLI

```bash
cd demos/contacts_cli
uv sync --extra dev
uv run contacts-cli create-sample input.sqlite
uv run contacts-cli run input.sqlite output.sqlite
```

The `run` command executes `contacts.normalize` through Tinnery Core and logs the
execution evidence (`trace_id`, `evidence_hash`).

### Run Tests

Root tests (Tinnery Core protocol + dual-entry acceptance):

```bash
uv sync --extra dev
uv run pytest -v
```

Demo tests (host CLI layers):

```bash
cd demos/contacts_cli
uv run pytest -v
```

## Documentation

- **Vision:** [`logos/VISION.md`](logos/VISION.md) — Long-term direction
- **Intent:** [`logos/intent.md`](logos/intent.md) — Current commitments
- **Decisions:** [`logos/decisions.md`](logos/decisions.md) — Accepted decisions (D-001)
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
