# Tinnery — Vision

## Purpose

Tinnery is a FlowHub that constrains, executes, verifies, and version-controls AI-assisted engineering work.

It enables CLI applications to delegate bounded engineering tasks to Tinnery, where AI can experiment, develop, and verify candidate implementations in isolation. Accepted artifacts are then returned to the host CLI through a shared protocol.

## Core Idea

**Host Application (CLI)** ↔ **Tinnery (FlowHub)**

- **CLI** owns business logic, data, and production operations
- **Tinnery** manages the engineering lifecycle: intent → scope → isolated experiment → verification → accepted artifact
- **Shared Protocol** allows CLI's transformation logic to be seamlessly loaded, executed, and versioned by Tinnery

The host application retains ownership. Tinnery delivers verified, versioned artifacts—not uncontrolled code changes.

## First Demonstration

A simple SQLite CLI that reads a contact table and produces a normalized contact table.

The demonstration validates:
- Can Tinnery constrain AI's experiment scope?
- Can candidate code be developed in isolation?
- Can results be independently verified?
- Can accepted artifacts be returned to CLI through explicit interfaces?
- Can the same artifact be reproducibly executed?

## Boundaries

**Does:**
- Manage bounded engineering flows
- Isolate AI experiments from production
- Verify results independently
- Deliver versioned, accepted artifacts

**Does Not (initially):**
- Universal multi-database framework
- General-purpose DAG scheduler
- Automatic production deployment
- Require Dagster or other execution platforms

## Guiding Principle

**Constrain the experiment, verify the result, preserve the evidence, release only accepted artifacts.**

Architecture grows only when evidence demands it.
