# Tinnery — Vision

Tinnery provides a shared Flow protocol and governance layer for CLI applications.

A business Flow remains owned by its host application while becoming discoverable and executable by Tinnery through the same explicit protocol. Business logic is defined once, not duplicated between the CLI and Flow Hub.

Multiple implementations of a Flow may coexist. Tinnery governs their AI-assisted development, isolated experimentation, independent verification, activation, and retirement. Only explicitly accepted versions are eligible for governed execution.

The host CLI and Tinnery must resolve implementations through the same versioned contract and execution boundary, allowing governed upgrades and rollbacks without duplicating business logic.

Tinnery governs only operations routed through this boundary; it does not automatically control arbitrary code or side effects outside enforced runtime constraints.

The first demonstration will prove that AI can develop and verify a candidate version, that Tinnery can govern its activation, and that the existing CLI can use it without rewriting its business logic.

**Principle:** Code may evolve continuously; executable status must be earned and explicitly governed.
