# Engineering / 工程

> **Type / 类型:** Engineering projection / 工程投影
> **Status / 状态:** Descriptive / 描述性
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Implemented in commit `7526b58`; verified by 26 root tests + 13 demo tests / 在提交 `7526b58` 实现；由 26 个根测试 + 13 个演示测试验证

> **Important / 重要:** This document describes observed and proposed engineering models. Only explicitly
> accepted decisions (see `logos/decisions.md`) have normative force. Proposed architecture is not an
> accepted engineering contract.
>
> **重要：** 本文档描述观察到的与提议的工程模型。只有明确接受的决策（见 `logos/decisions.md`）才具有规范效力。提议的架构不是已接受的工程契约。

---

## Current Systems / 当前系统

**Status:** P2 completed at commit `7526b58`. 26 root tests + 13 demo tests passing. CI verified.

**当前状态：** P2 在提交 `7526b58` 完成。26 个根测试 + 13 个演示测试通过。CI 已验证。

### Tinnery Core / Tinnery Core 包

```
tinnery/
├── contract.py      FlowContract + JSON Schema subset validator (fail-closed)
├── identity.py      ImplementationIdentity (source / bytecode / manifest digests)
├── runtime.py       bind_flow, BoundFlow, Executor, ExecutionReceipt
├── verification.py  verify_output, VerificationRecord
├── evidence.py      EvidenceJournal (append-only JSONL)
└── dagster/         Optional adapter (make_flow_op, make_flow_job)
```

See `engineering/flow-contract.md` for the full contract.

完整契约见 `engineering/flow-contract.md`。

### Host Demonstration / 宿主演示

**Status:** Adapted to `bind_flow` / 已适配 `bind_flow`

- **demos/contacts_cli/**: Contact normalization CLI with CLI → Task → Unit architecture
  - `units/normalize.py` — business implementation, **single source** / 业务实现，唯一来源
  - `units/database.py` — read-only source access, disposable target writes / 只读源访问、可弃目标写入
  - `flows.py` — `CONTACTS_FLOW = bind_flow(CONTACTS_CONTRACT, normalize_contacts)`
  - `tasks.py` — uses `Executor().invoke(CONTACTS_FLOW, contacts)`
- Uses Typer for CLI framework and UV for dependency management / 使用 Typer 作为 CLI 框架，UV 进行依赖管理
- Read-only source database enforced via SQLite URI mode / 通过 SQLite URI 模式强制只读源数据库
- 13 demo tests passing / 13 个演示测试通过

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
| Execution vs verification / 执行与验证 | A successful run is execution evidence, not a correctness verdict. 一次成功运行是执行证据，不是正确性判决。 |
| Verifier vs implementation / 验证器与实现 | A function must not certify its own output. Object identity is compared, not digests. 函数不得为自己的输出背书；比较对象身份而非摘要。 |
| Receipt vs data / 回执与数据 | Receipts store digests so the evidence log does not become a data dump. 回执只存摘要，避免证据日志变成数据转储。 |

### Dual Entry Status / 双入口现状

Both host CLI and Dagster invoke the same `BoundFlow` object (`CONTACTS_FLOW`):

宿主 CLI 与 Dagster 都调用同一个 `BoundFlow` 对象（`CONTACTS_FLOW`）：

- **Host CLI:** `tasks.py` calls `Executor().invoke(CONTACTS_FLOW, contacts)`
- **Dagster:** `make_flow_op(CONTACTS_FLOW)` creates an op that calls `Executor().invoke(bound_flow, payload)`

Both entries share:
- The same `FlowContract` (same `contract_sha256`)
- The same `ImplementationIdentity` (same `implementation_sha256`)
- The same business implementation (`normalize_contacts`)

Tests verify this in `tests/test_dual_entry.py`.

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
| A function cannot certify itself / 函数不能自我认证 | `verification.py` | `verifier is flow.implementation` → REJECTED |
| A failed execution can never verify as PASS / 失败执行不能验证为 PASS | `verification.py` | Non-SUCCEEDED → SKIPPED / 非成功即跳过 |
| Verification must name its checks / 验证必须具名检查项 | `verification.py` | Empty/non-string → ValueError / 空或非字符串即报错 |
| Unimplemented schema keywords must fail loudly / 未实现的关键字必须响亮失败 | `contract.py` | `ContractDefinitionError` / 抛定义错误 |
| Rejection is the default state / 拒绝是默认状态 | `runtime.py` | `status = "REJECTED"` as initial value / 状态初始值即拒绝 |
| Identity drift is detected before execution / 身份漂移在执行前检测 | `runtime.py` | Fresh identity compared to bind-time snapshot / 新身份与绑定快照比对 |
| Payloads are isolated from the caller / 载荷与调用方隔离 | `runtime.py` | JSON round-trip deep copy / JSON 往返深拷贝 |
| No partial output on failure / 失败不产生部分输出 | `runtime.py` | `output` forced to `None` / 输出强制为 None |
| Evidence minimizes data exposure / 证据最小化数据暴露 | `runtime.py` | Digests only, no payloads / 只存摘要 |
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
| What are remote invocation semantics: deadline, idempotency, retry, outcome-unknown? / 远程调用语义是什么：超时、幂等、重试、结果未知？ | Any non-local provider / 任何非本地 Provider |

---

## Operational Contracts / 运行契约

（暂无 / None）
