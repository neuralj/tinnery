# Project Decisions / 项目决策

> **Type / 类型:** Decision collection / 决策集合
> **Status / 状态:** No decisions yet / 暂无决策
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Tinnery project decisions / Tinnery 项目决策

---

## Decision Model / 决策模型

Decision lifecycle status and implementation status are independent dimensions.

决策生命周期状态与实现状态是两个独立维度。

### Lifecycle Status / 生命周期状态

Determines normative force:

决定规范效力：

- **accepted**: 已接受，具备规范效力
- **candidate**: 候选，不具备规范效力
- **superseded**: 已被新 Decision 取代
- **unresolved**: 定义丢失或状态不明

### Realization / 实现状态

Describes actual implementation:

描述实际实现情况：

- **verified**: 已完全实现，有证据支持
- **partial**: 部分实现
- **unverified**: 未验证

### Conflict / 冲突

A conflict is a condition requiring resolution; it must not silently override an accepted decision.

冲突是需要解决的条件；不得悄悄覆盖已接受的决策。

---

## Accepted Decisions / 已接受的决策

（暂无）

---

## Candidate Decisions / 候选决策

### D-001 — Use Dagster as Tinnery's Initial Operator-Facing Entry Point / 采用 Dagster 作为 Tinnery 的初始操作入口

> **Type / 类型:** Decision
> **Lifecycle / 生命周期:** candidate / 候选
> **Realization / 实现状态:** unverified / 未验证
> **Scope / 范围:** project / 项目级
> **Proposed / 提议时间:** 2026-10-12

**Statement / 陈述:**

Use Dagster as the operation entry point for Tinnery's first version, rather than building a custom CLI, Web Server, or scheduler.

使用 Dagster 作为 Tinnery 第一版的操作入口，而不是自建 CLI、Web Server 或调度器。

**Key Clarifications / 关键澄清:**

1. Dagster provides Tinnery's initial operation interface, scheduling, and run monitoring.
   Dagster 提供 Tinnery 初期的操作界面、调度和运行监控。

2. Tinnery Core's Flow contracts, version identity, and invocation protocol remain independent and are not defined by Dagster.
   Tinnery Core 的 Flow 契约、版本身份及调用协议保持独立，不由 Dagster 定义。

3. `demos/contacts_cli/` is an independent host example that can run without installing or starting Dagster.
   `demos/contacts_cli/` 是独立宿主示例，可以不安装、不启动 Dagster。

4. Not building Tinnery's own CLI, Web Server, or generic scheduler initially is not a permanent prohibition against future alternative entry points.
   初期不建设 Tinnery 自有 CLI、Web Server 或通用调度器，不是永久禁止未来其他入口。

**Rationale / 理由:**

- Avoid duplicating existing capabilities / 避免重复建设已有能力
- Leverage Dagster's UI, scheduling, and execution monitoring / 利用 Dagster 的 UI、调度和执行监控
- Focus Tinnery on core protocol and governance / 让 Tinnery 专注于核心协议和治理

**Proposed P2 Direction / 提议的 P2 方向:**

Pending acceptance of D-001 and explicit P2 authorization, the proposed direction is:
在 D-001 被接受和 P2 被明确授权之前，提议的方向是：

- Tinnery Core Library: Flow contracts, version identity, invocation protocol, governance & evidence
  Tinnery Core 库：Flow 契约、版本身份、调用协议、治理与证据

- Dagster Integration: Map Dagster's run requests to Tinnery's Flow invocations
  Dagster 集成：将 Dagster 的运行请求映射为 Tinnery 的 Flow 调用

- Host Provider: Invoke host-owned business implementations without duplicating business logic
  宿主 Provider：调用宿主拥有的实际业务实现，不复制业务逻辑

This direction is proposed, not yet accepted or authorized.
此方向是提议，尚未被接受或授权。

**Status / 状态:** Candidate — requires explicit acceptance before P2 implementation / 候选 — 需要明确接受后才能实施 P2
