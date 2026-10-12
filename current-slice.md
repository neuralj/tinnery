# Current Slice — Shared Flow Lifecycle with a Contact CLI

> **Type:** Validation Slice  
> **Status:** Proposed  
> **Scope:** In-repository demonstration  
> **Related Goal:** G-01 — Validate the Shared Flow Lifecycle (`Candidate`)  
> **Authority:** This document proposes an experiment; it does not itself accept G-01 or authorize production execution.

---

## Current Execution Authorization / 当前执行授权

**Overall Slice Status / 整体切片状态:** Proposed / 提案中  
**Related Goal / 相关目标:** G-01 — Candidate / 候选

### Current Phase / 当前阶段: P1 — Host CLI Baseline / 宿主 CLI 基线

**P1 Status / P1 状态:** Completed / 已完成  
**Authorization / 授权:** Authorized — P1 scope only / 已授权 — 仅限 P1 范围  
**Completion / 完成时间:** 2026-10-12  
**Evidence / 证据:** 
- 13 tests passing locally / 本地 13 个测试通过
- CI verified on GitHub Actions (push events) / CI 在 GitHub Actions 上验证（push 事件）
- PR trigger: not yet verified / PR 触发：尚未验证
- Failure scenario: not yet verified / 失败场景：尚未验证

#### P1 Objective / P1 目标

Establish a small, independently runnable SQLite contact-normalization CLI before designing the shared Flow protocol.

在设计共享 Flow 协议之前，建立一个小型、可独立运行的 SQLite 联系人标准化 CLI。

#### P1 Scope / P1 范围

- `demos/contacts_cli/`
- `.github/workflows/ci.yml` — CI verification infrastructure / CI 验证基础设施
- Directly related tests within the demonstration scope / 演示范围内的直接相关测试
- Necessary governance document updates / 必要的治理文档更新

#### P1 Acceptance Criteria / P1 验收标准

- Read synthetic contacts from a SQLite source / 从 SQLite 源读取合成联系人
- Normalize records using a deterministic, independently testable function / 使用确定性、可独立测试的函数标准化记录
- Write to a separate, disposable SQLite output database / 写入独立、可丢弃的 SQLite 输出数据库
- Keep transformation logic independent of database access and persistence / 保持转换逻辑独立于数据库访问和持久化
- Verify expected field values, keys, record counts, invalid-input behavior, repeated execution, and failure atomicity / 验证预期字段值、键、记录数、无效输入行为、重复执行和失败原子性
- Provide reproducible run and test instructions / 提供可重现的运行和测试说明

#### P1 Out of Scope / P1 范围外

- Tinnery Flow protocol implementation / Tinnery Flow 协议实现
- Version registry or candidate activation / 版本注册表或候选激活
- Rollback mechanisms / 回滚机制
- General-purpose scheduler or workflow UI / 通用调度器或工作流 UI

---

### Future Phases (Not Yet Authorized) / 未来阶段（尚未授权）

**P3 — Version Governance / 版本治理:** Verify candidate version isolation, independent acceptance, explicit activation, deactivation, rollback, and execution traceability.

验证候选版本隔离、独立接受、显式激活、停用、回滚和执行可追溯性。

---

### Current Phase / 当前阶段: P2 — Shared Flow Protocol / 共享 Flow 协议

**P2 Status / P2 状态:** Completed / 已完成  
**Authorization / 授权:** Authorized — P2 scope only / 已授权 — 仅限 P2 范围  
**Start Time / 开始时间:** 2026-10-12  
**Completion / 完成时间:** 2026-10-12  
**Evidence / 证据:**
- 26 root tests (protocol + dual-entry acceptance) and 13 demo tests passing locally / 本地 26 个根测试（协议 + 双入口验收）与 13 个演示测试通过
- Core API: FlowContract.define + bind_flow + Executor + ExecutionReceipt + verify_output
- Dual-entry shared implementation verified: host CLI and Dagster use same BoundFlow / 双入口共享实现已验证：宿主 CLI 与 Dagster 使用同一 BoundFlow
- Implementation identity: module_source_sha256 + callable_code_sha256 (bytecode disassembly) / 实现身份：源模块哈希 + 字节码反汇编哈希
- Contract digest: stable SHA256 of canonical JSON / 契约摘要：规范 JSON 的稳定 SHA256
- Independent verification: verify_output with self-certification prevention / 独立验证：verify_output 禁止自认证
- All acceptance criteria met / 全部验收标准已满足

#### P2 Objective / P2 目标

Prove that the native CLI and Dagster invoke the same business implementation through a shared versioned contract, with Tinnery Core providing Flow identity, invocation protocol, and execution evidence.

证明原生 CLI 和 Dagster 通过共享的版本化契约调用相同的业务实现，Tinnery Core 提供 Flow 身份、调用协议和执行证据。

#### P2 Scope / P2 范围

- `tinnery/` — Tinnery Core Library (Flow contracts, invocation protocol, provider interface, execution evidence)
  Tinnery Core 库（Flow 契约、调用协议、Provider 接口、执行证据）
- `tinnery/dagster/` — Dagster Integration (Resources, Ops, Jobs)
  Dagster 集成（Resources、Ops、Jobs）
- `demos/contacts_cli/` — Host CLI integration with Tinnery Core
  宿主 CLI 与 Tinnery Core 的集成
- `tests/` — Verification tests for dual-entry shared implementation
  双入口共享实现的验证测试
- `engineering/flow-contract.md` — Flow Contract specification
  Flow 契约规范

#### P2 Acceptance Criteria / P2 验收标准

- Define Flow identity and contract (flow_id, version, contract_version)
  定义 Flow 身份与契约（flow_id、version、contract_version）
- Define typed invocation request and result
  定义类型化调用请求与结果
- Host CLI invokes business implementation through Tinnery Core
  宿主 CLI 通过 Tinnery Core 调用业务实现
- Dagster invokes the same business implementation through Dagster Integration
  Dagster 通过 Dagster Integration 调用相同的业务实现
- Both entries record execution evidence (flow_id, version, implementation_hash)
  两个入口都记录执行证据（flow_id、version、implementation_hash）
- Verify no duplicate business implementation
  验证没有重复业务实现

#### P2 Out of Scope / P2 范围外

- Version registry or candidate activation / 版本注册表或候选激活
- Rollback mechanisms / 回滚机制
- Plugin frameworks (Entry Points, Pluggy, Stevedore) / 插件框架
- Generic scheduler or workflow UI / 通用调度器或工作流 UI

---

**Authorization Rule / 授权规则:** Passing P1 does not automatically authorize P2, P3, or acceptance of G-01. All phase transitions require explicit authorization.

通过 P1 不会自动授权 P2、P3 或接受 G-01。所有阶段转换都需要明确授权。

---

## 1. Objective

Test whether one versioned business Flow can be invoked by both a host CLI and Tinnery through the same explicit contract, while Tinnery supports isolated candidate experimentation, independent verification, and controlled version activation and rollback.

The experiment must test the shared protocol and governance boundary—not merely prove that a contact-normalization function works.

## 2. Demonstration Host

Create a small contact-normalization CLI under `demos/contacts_cli/` in the Tinnery repository.

This is an explicit demonstration-only host application colocated with Tinnery to reduce setup cost. It is not part of the Tinnery core package and does not imply that future host CLIs must share the same repository or deployment.

The example owns the contact domain logic. Tinnery must not contain a second implementation of that logic, and the Tinnery core must not depend on or import the example as a built-in domain implementation.

## 3. Scenario

The host CLI reads synthetic contacts from a SQLite source table, normalizes them, and writes the results to a SQLite target table in an isolated demo workspace.

- **Input:** `input.sqlite: raw_contacts`, opened through a read-only source boundary.
- **Output:** `output.sqlite: normalized_contacts`, written only to a disposable target database/table for this experiment.

**Isolation choice:** Use separate source and target SQLite files in this first slice so the canonical input can be checked independently and is not the write target. Writing to a second table in the same SQLite file is a possible later variation, but must not be described as strongly isolated merely because separate connections are used.

**Transformation:** A deterministic function receives records and returns normalized records. It does not open databases, execute SQL, select versions, or persist output.

- **Initial version:** V1 is the known accepted baseline for the demo.
- **Candidate version:** V2 is developed with AI assistance and remains isolated until verification and explicit activation.

**Invocation:** Native CLI and Tinnery use the same Flow contract and the same version-resolution/call boundary. The CLI must not hard-code a separate V1 implementation.

Use synthetic, bounded fixtures only. No production database, credential, or business data is in scope.

### Initial Transformation Contract (proposed for this slice)

- Preserve `contact_id` as the stable output key.
- Normalize `full_name` by trimming leading/trailing whitespace and collapsing consecutive whitespace to one space. Reject null or empty normalized names.
- Normalize `email` by trimming leading/trailing whitespace and converting letters to lowercase. Reject null or empty normalized emails.
- Produce exactly one output row per valid input contact.
- Validate the complete input before mutating the target. If any contact is invalid, fail the batch and leave the target unchanged.
- Re-running the same valid input must not create duplicate keys or change the normalized business values.

Use a small deterministic fixture such as `" Alice   Chen " / " ALICE@EXAMPLE.COM "` → `"Alice Chen" / "alice@example.com"`. The final fixture and exact acceptance assertions must be committed with the implementation before the slice can pass.

## 4. Minimal Lifecycle to Demonstrate

1. Run the baseline V1 through the native CLI and retain its observable result.
2. Develop V2 with AI assistance without overwriting the accepted V1.
3. Execute V2 in an isolated experiment with bounded inputs and a disposable output target.
4. Independently verify V2's output and compare it with the contract and V1 where comparison is meaningful.
5. Activate V2 only through an explicit acceptance step.
6. Run the native CLI again and verify that it resolves and invokes V2 through the shared boundary.
7. Revoke activation or roll back to V1, run the CLI again, and verify the actual implementation used.

AI-assisted development in this slice does not require integrating an LLM service or building an autonomous coding agent into Tinnery. The AI may participate in the engineering workflow that creates V2; Tinnery's own automated AI-agent orchestration is out of scope.

## 5. Acceptance Criteria

The slice passes only when the evidence demonstrates all applicable criteria below:

- **Shared implementation:** CLI and Tinnery invoke the same identified Flow implementation through the same versioned contract; the demo does not duplicate business logic.
- **Version traceability:** Every run records the resolved Flow/version identity, selected execution path, and result status.
- **Isolation:** Candidate execution uses synthetic bounded input and disposable output. The canonical input fixture remains unchanged.
- **Independent verification:** A verifier separate from the transformation checks expected normalized values, key uniqueness, record counts, invalid-input behavior, and repeated-run behavior.
- **Failure atomicity:** Invalid input fails the batch without leaving partial target results for that batch.
- **Controlled activation:** V2 cannot become the CLI's active version merely because it exists or its own execution reports success; activation requires an explicit acceptance action.
- **Rollback:** After rollback, the CLI again resolves V1, and run evidence confirms which version actually executed.
- **Observable execution:** A run produces inspectable status and result evidence, including version identity and verification outcome. A full web UI is not required in this slice.
- **No production effects:** No production service, data source, or deployment target is accessed or modified.

The proposed contract above is the starting point for implementation. If its business semantics are changed, record the change explicitly before updating the acceptance tests; do not silently weaken expected behavior to make a candidate pass.

## 6. Scope Limits / Non-goals

This slice does not aim to deliver:

- A universal ETL or multi-database framework.
- A general-purpose DAG engine or production scheduler.
- A web-based visual editor or full workflow UI.
- A built-in LLM service or autonomous AI-coding agent.
- Production deployment, automatic promotion, or production data writes.
- A general plugin marketplace, multi-language RPC framework, or distributed worker system.
- A claim that arbitrary candidate code is secure merely because it follows the Flow contract.

The demo may use the smallest mechanism sufficient to test the protocol. Any mechanism chosen here must be recorded as provisional unless explicitly accepted as a project decision.

## 7. Constraints

- Domain logic remains owned by `demos/contacts_cli/`.
- The transformation receives data and returns data; database access and persistence remain outside it.
- The candidate must not receive unrestricted source/target database handles through the transformation interface.
- Source access is read-only; candidate writes are restricted to disposable output.
- Version selection and activation must be explicit and observable, not hidden in CLI-specific branching.
- An execution-success status is not an independent correctness verdict.
- Governance guarantees apply only to operations that actually pass through the enforced demo execution boundary. If the candidate can bypass that boundary, the slice must not claim stronger isolation than the evidence supports.

## 8. Stop Conditions

Stop and report the unresolved issue if any of the following occurs:

- The CLI and Tinnery require separate copies of the business logic to work.
- The CLI bypasses the shared version-resolution/call boundary.
- V2 can overwrite or alter V1 before explicit activation.
- The experiment cannot keep candidate output separate from the canonical input fixture.
- The verifier merely repeats the transformation's own success claim instead of checking output independently.
- The actual implementation/version used by a run cannot be identified.
- Isolation or permitted side effects cannot be established with evidence.
- The implementation requires introducing a broad framework whose need is not demonstrated by this slice.

A stop condition is a valid result. Do not silently weaken the contract to obtain a passing demo.

## 9. Evidence to Retain

Retain only evidence needed to reproduce and assess this slice:

- The exact Flow contract and its version.
- The identity/hash of each tested implementation version.
- The synthetic input fixture identity and confirmation that the canonical input remained unchanged.
- The resolved version and status for each CLI/Tinnery run.
- The verifier's results, including output comparison and invalid-input/failure-atomicity tests.
- Activation and rollback actions, plus evidence of the version used afterward.
- Commands or test instructions required to reproduce the result.

## 10. Decision After the Slice

After verification, explicitly decide whether to:

- accept G-01 or revise/reject it;
- accept any protocol or governance decisions demonstrated by the experiment;
- revise the slice because evidence exposed a missing requirement; or
- start a separate slice for scheduling and richer visual inspection.

Passing this slice does not automatically accept every architectural choice made during implementation, nor does it establish production readiness.
