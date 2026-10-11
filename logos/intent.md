# Project Intent / 项目意图

> **Type / 类型:** Intent
> **Status / 状态:** Candidate / 候选
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Tinnery project commitments / Tinnery 项目承诺

---

## Commitment / 当前承诺

Establish a shared, versioned Flow protocol and governance mechanism through which a host CLI and Tinnery can use the same business implementation, while Tinnery supports AI-assisted experimentation, independent verification, observable execution, and controlled version activation.

建立一套共享的、具有明确版本的 Flow 协议与治理机制，使宿主 CLI 和 Tinnery 能够使用同一份业务实现，同时由 Tinnery 支持 AI 辅助实验、独立验证、可观察执行和受控版本激活。

---

## Goals / 目标

### G-01 — Validate the Shared Flow Lifecycle / 验证共享 Flow 的生命周期

**Status / 状态:** Candidate / 候选

Validate the following lifecycle through a small host CLI demonstration and a bounded data transformation scenario.

通过一个小型宿主 CLI 演示和一个有界的数据转换场景，验证以下生命周期：

- The CLI and Tinnery use the same business implementation and versioned contract.
  CLI 与 Tinnery 使用同一份业务实现和版本化契约。
- AI can create, execute, and compare candidate implementations in an isolated environment.
  AI 可以在隔离环境中创建、运行和比较候选实现。
- The correctness of candidate implementations can be assessed through independent verification.
  候选实现的正确性能够通过独立验证进行判断。
- Version activation, deactivation, and rollback are explicitly controlled and traceable.
  版本激活、撤销激活和回滚可以被明确控制并追溯。
- Execution processes and results are sufficiently observable.
  执行过程及结果具有足够的可观察性。

Formal acceptance of this Goal and its acceptance criteria are defined by the current-slice contract.

本 Goal 的正式接受和验收标准由当前切片契约确定。

---

## Non-goals / 非目标

- Building a universal ETL or multi-database framework in the first slice.
  在首个切片中建立通用 ETL 或多数据库框架。
- Building a complete DAG scheduling platform before the core protocol has been validated.
  在核心协议尚未验证前，自行构建完整的 DAG 调度平台。
- Automatically promoting AI-generated code to production.
  自动将 AI 生成的代码发布到生产环境。
- Duplicating business logic owned by host applications.
  复制宿主应用拥有的业务逻辑。

---

## Constraints / 约束

- Business logic remains owned by the host application and must not be duplicated merely to integrate with Tinnery.
  业务逻辑归宿主应用所有，不因接入 Tinnery 而重复实现。
- Candidate implementations must not modify stable versions or production data without authorization.
  候选实现不得未经授权修改稳定版本或生产数据。
- Execution scope, permitted side effects, and implementation identity must be explicit.
  执行范围、允许的副作用与实现版本身份必须明确。
- Successful execution does not establish business correctness; candidate implementations must not self-certify.
  运行成功不等于业务正确；候选实现不得自我认证。
- Only explicitly accepted and authorized implementations are eligible for governed execution.
  只有经过明确接受和授权的实现，才有资格进入受治理的正式执行路径。
- Governance guarantees apply only to operations routed through an enforced execution boundary.
  治理保证只覆盖通过受控执行边界的操作。
- Version switches must preserve historical evidence; retired versions remain traceable.
  版本切换必须保留历史证据；被撤销的版本仍可追溯。

---

## Principles / 原则

1. **Distinguish Intent, Decision, Reality, and Evidence.**
   **明确区分 Intent、Decision、Reality 与 Evidence。**
2. **Unaccepted assumptions must not become normative constraints.**
   **未接受的假设不得成为规范性约束。**
3. **Do not infer correctness beyond the available evidence from code existence, passing tests, or successful execution.**
   **不得仅凭代码存在、测试通过或执行成功，推断超出已有证据范围的正确性。**
4. **Validate core hypotheses before adding architecture and abstractions.**
   **先验证核心假设，再增加架构和抽象。**
5. **Keep current Goals few and verifiable; unaccepted candidate Goals are not binding.**
   **当前目标必须少而可验收；未接受的候选目标不具约束力。**

---

## Current Slice / 当前切片

See `current-slice.md` for the currently authorized engineering scope, acceptance criteria, verification evidence, and stop conditions.

当前获准的工程范围、验收标准、验证证据及停止条件，参见 `current-slice.md`。
