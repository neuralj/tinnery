# Engineering / 工程

> **Type / 类型:** Engineering projection / 工程投影
> **Status / 状态:** Descriptive / 描述性
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Observed implementation; proposed models; not accepted Decisions / 依据实际实现与提议模型；非已接受决策

> **Important / 重要:** This document describes observed and proposed engineering models. Only explicitly
> accepted decisions (see `logos/decisions.md`) have normative force. Proposed architecture is not an
> accepted engineering contract.
>
> **重要：** 本文档描述观察到的与提议的工程模型。只有明确接受的决策（见 `logos/decisions.md`）才具有规范效力。提议的架构不是已接受的工程契约。

---

## Current Systems / 当前系统

**Status:** Working tree implements the `bind_flow` design; root acceptance tests absent / 工作树实现了 `bind_flow` 设计；根验收测试缺失

### Tinnery Core / Tinnery Core 包

```
tinnery/
├── contract.py      FlowContract + JSON Schema subset validator (fail-closed)
├── identity.py      ImplementationIdentity (source / bytecode / manifest digests)
├── runtime.py       bind_flow, BoundFlow, Executor, ExecutionReceipt
├── verification.py  verify_output, VerificationRecord
├── evidence.py      EvidenceJournal (append-only JSONL)
└── dagster/         Optional adapter (ops.py migrated, jobs.py not)
```

See `engineering/flow-contract.md` for the full contract, and `reality/project.md` for observed state
including two known implementation defects.

完整契约见 `engineering/flow-contract.md`；观察状态（含两处已知实现缺陷）见 `reality/project.md`。

### Host Demonstration / 宿主演示

**Status:** Adapted to `bind_flow` / 已适配 `bind_flow`

- **demos/contacts_cli/**: Contact normalization CLI with CLI → Task → Unit architecture
  - `units/normalize.py` — business implementation, **single source** / 业务实现，唯一来源
  - `units/database.py` — read-only source access, disposable target writes / 只读源访问、可弃目标写入
  - `flows.py`, `tasks.py` — adapted to bind the host function to a Flow contract / 已适配为绑定宿主函数到 Flow 契约
- Uses Typer for CLI framework and UV for dependency management / 使用 Typer 作为 CLI 框架，UV 进行依赖管理
- Read-only source database enforced via SQLite URI mode / 通过 SQLite URI 模式强制只读源数据库

**Observation:** The 13 demo tests were not executed in the 2026-10-12 observation.
**观察：** 13 个演示测试在 2026-10-12 的观察中未执行。

---

## Execution Model / 执行模型

The current Core implements a three-stage pipeline in which **each stage produces a separate artifact**.

当前 Core 实现三段流水线，**每段产出独立产物**。

```
Host-owned function / 宿主函数
        |
        v
bind_flow(contract, function)          -> BoundFlow (contract + snapshot identity)
        |
        v
Executor.invoke(flow, payload)         -> ExecutionReceipt
                                              (status SUCCEEDED|FAILED|REJECTED,
                                               failure_code, digests, runtime info)
        |
        |   ← separate function, separate object, cannot overwrite the above
        v
verify_output(flow, result, verifier)  -> VerificationRecord
                                              (status PASS|FAIL|SKIPPED|REJECTED,
                                               verifier digests, named checks)
        |
        v
EvidenceJournal (JSONL)
```

### Why the stages are separate / 为什么分段

| Separation / 分离 | Reason / 理由 |
|---|---|
| Execution vs verification / 执行与验证 | A successful run is execution evidence, not a correctness verdict. Low-level mechanisms cannot establish end-to-end correctness on their own. 一次成功运行是执行证据，不是正确性判决；底层机制本身无法建立端到端正确性。 |
| Verifier vs implementation / 验证器与实现 | A function must not certify its own output. Object identity is compared, not digests. 函数不得为自己的输出背书；比较对象身份而非摘要。 |
| Receipt vs data / 回执与数据 | Receipts store digests so the evidence log does not become a data dump. 回执只存摘要，避免证据日志变成数据转储。 |

### Dual Entry Status / 双入口现状

The previously implemented design routed both a host CLI and Dagster through a `Provider` protocol.
That code (`tinnery/provider.py`, `tinnery/invocation.py`, `tinnery/core.py`) has been deleted from the
working tree.

此前实现的设计让宿主 CLI 与 Dagster 都走 `Provider` 协议。该代码（`tinnery/provider.py`、
`tinnery/invocation.py`、`tinnery/core.py`）已从工作树删除。

Current state / 当前状态:

- `tinnery/dagster/ops.py` imports `BoundFlow`/`Executor` from `tinnery.runtime` — **migrated**
  `tinnery/dagster/ops.py` 已导入新 Core API — **已迁移**
- `tinnery/dagster/jobs.py` — **not migrated**; fails to import without the optional `dagster` extra
  `tinnery/dagster/jobs.py` — **未迁移**；无 `dagster` 可选依赖时导入失败
- `tests/test_dual_entry.py` — **deleted**; the dual-entry acceptance evidence no longer exists
  **已删除**；双入口验收证据已不存在

Dagster remains an **optional transport adapter**, not a required dependency of Core. This is consistent
with D-001's clarification that Flow semantics are defined independently of Dagster.

Dagster 仍是**可选传输适配器**，不是 Core 的必需依赖。这与 D-001 中「Flow 语义独立于 Dagster 定义」的澄清一致。

---

## Component Responsibilities / 组件职责

| Component / 组件 | Responsible For / 负责 | Not Responsible For / 不负责 |
|---|---|---|
| Tinnery Core | Flow contracts, implementation identity, execution receipts, verification records / Flow 契约、实现身份、执行回执、验证记录 | Owning business logic; building schedulers; enforcing runtime isolation / 拥有业务逻辑；构建调度器；强制运行期隔离 |
| Host Application | Owning business code and domain semantics / 拥有业务代码与领域语义 | Duplicating business implementation inside Core / 在 Core 内复制业务实现 |
| Verifier | Independently checking output against expectations / 独立检查输出是否符预期 | Certifying its own output / 为自己的输出背书 |
| Dagster (optional) | Scheduling and run monitoring, if adopted / 若采用，负责调度与运行监控 | Defining Flow semantics / 定义 Flow 语义 |

---

## Engineering Invariants / 工程不变量

These are the properties the current design is built to preserve. Each is anchored to a location in
the source; each is falsifiable.

以下是当前设计意图保持的性质。每条都对应源码位置，每条都可被证伪。

| Invariant / 不变量 | Anchored in / 位置 | Mechanism / 机制 |
|---|---|---|
| An execution-success status is not a correctness verdict / 执行成功不是正确性判决 | `verification.py` | Separate function and separate record / 独立函数与独立记录 |
| A function cannot certify itself / 函数不能自我认证 | `verification.py:65-67` | `verifier is flow.implementation` → REJECTED |
| A failed execution can never verify as PASS / 失败执行不能验证为 PASS | `verification.py:50-51` | Non-SUCCEEDED → SKIPPED / 非成功即跳过 |
| Verification must name its checks / 验证必须具名检查项 | `verification.py:72-73` | Empty/non-string → ValueError / 空或非字符串即报错 |
| Unimplemented schema keywords must fail loudly / 未实现的关键字必须响亮失败 | `contract.py:58-61` | `ContractDefinitionError` / 抛定义错误 |
| Rejection is the default state / 拒绝是默认状态 | `runtime.py:92` | `status = "REJECTED"` as initial value / 状态初始值即拒绝 |
| Identity drift is detected before execution / 身份漂移在执行前检测 | `runtime.py:114-119` | Fresh identity compared to bind-time snapshot / 新身份与绑定快照比对 |
| Payloads are isolated from the caller / 载荷与调用方隔离 | `runtime.py` | JSON round-trip deep copy / JSON 往返深拷贝 |
| No partial output on failure / 失败不产生部分输出 | `runtime.py:174` | `output` forced to `None` / 输出强制为 None |
| Evidence minimizes data exposure / 证据最小化数据暴露 | `runtime.py` `ExecutionReceipt` | Digests only, no payloads / 只存摘要 |
| Domain logic is not duplicated / 领域逻辑不重复 | `demos/contacts_cli/contacts_cli/units/normalize.py` | Single source; Core never imports the host / 唯一来源；Core 不 import 宿主 |

---

## Engineering Constraints / 工程约束

**Status: Observed / 状态：观察所得**

- Synthetic test data only / 仅使用合成测试数据
- Source data read-only (enforced via SQLite URI mode) / 源数据只读（通过 SQLite URI 模式强制）
- Output in disposable target / 输出在可丢弃目标中
- Transformation logic independent of database access / 转换逻辑独立于数据库访问
- Tinnery Core protocol remains independent of any scheduler / Tinnery Core 协议独立于任何调度器
- Zero third-party dependencies in `tinnery/` core modules / `tinnery/` 核心模块零第三方依赖
- Python standard library only in the Core / Core 仅用 Python 标准库

**Declared but not enforced / 已声明但未强制:**

- `FlowContract.effects_enforced` is `False`. There is no sandbox, no OS-level permission control, no
  container. Any statement about isolation must state which execution boundary it refers to.
  `FlowContract.effects_enforced` 为 `False`。没有沙箱、没有 OS 级权限控制、没有容器。
  任何关于隔离的陈述都必须指明它指的是哪个执行边界。

**Note on Technology Choices / 关于技术选择的说明:**

Typer and UV are used in the host demonstration, but they are not architectural constraints for
Tinnery Core. Dagster is an optional extra (`pyproject.toml` → `optional-dependencies.dagster`).

Typer 和 UV 在宿主演示中使用，但不是 Tinnery Core 的架构约束。Dagster 是可选依赖。

---

## Open Engineering Questions / 待解决的工程问题

These are not answered by the current design. Each requires a decision before the corresponding
mechanism can be claimed.

当前设计未回答以下问题。每项都需要决策才能主张对应机制。

| Question / 问题 | Blocks / 阻塞 |
|---|---|
| What is the threat model for candidate execution: accidental bug, prompt-injected code, or actively malicious code? / 候选执行的威胁模型是什么：意外 bug、提示注入、还是主动恶意？ | Any sandbox or isolation claim / 任何沙箱或隔离主张 |
| What evidence is sufficient for acceptance/activation, and which authority approves, revokes, or rolls back? / 什么证据足以接受/激活，谁能批准、撤销、回滚？ | Version governance (P3) / 版本治理（P3） |
| How is the evidence journal protected against editing or truncation? / 证据日志如何防止被编辑或截断？ | Any audit-grade claim / 任何审计级主张 |
| How are dependency closure and native library identity captured across Python environments? / 如何跨环境捕获依赖闭包与原生库身份？ | Supply-chain completeness / 供应链完整性 |
| How is it demonstrated that two entry points resolved the same source and implementation identity? / 如何证明两个入口解析到相同的源身份与实现身份？ | Dual-entry acceptance / 双入口验收 |
| What are remote invocation semantics: deadline, idempotency, retry, outcome-unknown? / 远程调用语义是什么：超时、幂等、重试、结果未知？ | Any non-local provider / 任何非本地 Provider |

---

## Operational Contracts / 运行契约

（暂无 / None）
