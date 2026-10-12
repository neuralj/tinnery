# Engineering / 工程

> **Type / 类型:** Engineering projection / 工程投影
> **Status / 状态:** Descriptive / 描述性
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Proposed engineering models / 提议的工程模型

> **Important / 重要:** This document describes proposed engineering models and constraints. Only explicitly accepted decisions (see `logos/decisions.md`) have normative force. Proposed architecture is not an accepted engineering contract.
>
> **重要：** 本文档描述提议的工程模型和约束。只有明确接受的决策（见 `logos/decisions.md`）才具有规范效力。提议的架构不是已接受的工程契约。

---

## Current Systems / 当前系统

**Status:** P1 demonstration completed / P1 演示已完成

- **demos/contacts_cli/**: Contact normalization CLI with CLI → Task → Unit architecture
  - 13 tests passing locally / 本地 13 个测试通过
  - CI verified on GitHub Actions (push events) / CI 在 GitHub Actions 上验证（push 事件）
  - Read-only source database enforced via SQLite URI mode / 通过 SQLite URI 模式强制只读源数据库
  - Uses Typer for CLI framework and UV for dependency management / 使用 Typer 作为 CLI 框架，UV 进行依赖管理

---

## Target Architecture / 目标架构

**Status: Proposed / 状态：提议**

### Dual-Entry Structure / 双入口结构

```
                    Dagster UI (Operation Entry / 操作入口)
                        |
                Dagster Integration (Mapping Layer / 映射层)
                        |
Host CLI -------- Tinnery Core Contract (Shared Protocol / 共享协议)
                        |
                 Typed Provider (Invocation Boundary / 调用边界)
                        |
              Host Business Implementation (Domain Logic / 领域逻辑)
```

This diagram expresses shared invocation contracts, not that all invocations must go through Dagster.
此图表达的是调用契约共享，而不是所有调用都必须经过 Dagster。

### Component Responsibilities / 组件职责

| Component / 组件 | Responsible For / 负责 | Not Responsible For / 不负责 |
|-----------------|------------------------|------------------------------|
| Dagster | UI, scheduling, execution monitoring, run lifecycle | Defining Tinnery's Flow semantics / 定义 Tinnery 的 Flow 语义 |
| Tinnery Core | Flow contracts, version identity, invocation protocol, governance & evidence | Building generic scheduler / 构建通用调度器 |
| Provider | Mapping contracts to actual business implementations / 将契约映射到实际业务实现 | Defining business rules / 定义业务规则 |
| Host Application | Owning business code and domain semantics / 拥有业务代码和领域语义 | Duplicating business implementation for Tinnery / 为 Tinnery 复制业务实现 |

---

## Engineering Constraints / 工程约束

**Status: Proposed / 状态：提议**

- Synthetic test data only / 仅使用合成测试数据
- Source data read-only (enforced via SQLite URI mode) / 源数据只读（通过 SQLite URI 模式强制）
- Output in disposable target / 输出在可丢弃目标中
- Transformation logic independent of database access / 转换逻辑独立于数据库访问
- Tinnery Core protocol must remain independent of Dagster execution model / Tinnery Core 协议必须独立于 Dagster 执行模型

**Note on Technology Choices / 关于技术选择的说明:**

Typer and UV are used in the current P1 demonstration (`demos/contacts_cli/`), but they are not mandatory architectural constraints for Tinnery Core. Technology choices for Tinnery Core will be determined during P2 implementation based on actual requirements.

Typer 和 UV 在当前 P1 演示（`demos/contacts_cli/`）中使用，但不是 Tinnery Core 的强制架构约束。Tinnery Core 的技术选择将在 P2 实施期间根据实际需求确定。

---

## Operational Contracts / 运行契约

（暂无）
