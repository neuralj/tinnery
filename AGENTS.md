# Tinnery — Agent Entry

## Project Purpose / 项目目的

Tinnery is a shared Flow protocol and governance layer for CLI applications.

Tinnery 是 CLI 应用的共享 Flow 协议与治理层。

### What Tinnery Does / Tinnery 做什么

- Provides a shared Flow protocol for host CLIs and Tinnery to use the same business implementation
- Supports AI-assisted experimentation, independent verification, and controlled version activation
- Enables observable execution and traceable version governance

### What Tinnery Does Not Do / Tinnery 不做什么

- Does not own business logic (domain logic remains in host CLIs)
- Does not automatically promote AI-generated code to production
- Does not build universal ETL, DAG schedulers, or workflow UIs (initially)

---

## Logos — Semantic Authority / 语义权威

`logos/` contains the project's semantic authority. These files define what Tinnery is, what it commits to, and what has been decided.

`logos/` 包含项目的语义权威。这些文件定义了 Tinnery 是什么、承诺做什么、以及已做出的决策。

### Entry Points / 入口点

| File / 文件 | Purpose / 用途 | When to Read / 何时阅读 |
|------------|---------------|------------------------|
| `logos/VISION.md` | Long-term direction (Why) / 长期方向（为什么） | Before any design or review / 任何设计或审查之前 |
| `logos/intent.md` | Current commitments (Will) / 当前承诺（意愿） | Before implementation / 实现之前 |
| `logos/decisions.md` | Accepted decisions / 已接受的决策 | Before making architectural choices / 做架构选择之前 |
| `logos/reality.md` | Current observed state (Is) / 当前观察状态（是什么） | Before claiming what exists / 声称某物存在之前 |
| `logos/engineering.md` | Engineering constraints / 工程约束 | Before implementation / 实现之前 |

### Reading Order / 阅读顺序

1. Start with `logos/VISION.md` to understand the long-term direction
2. Read `logos/intent.md` to understand current commitments and constraints
3. Check `logos/decisions.md` for accepted decisions
4. Review `logos/reality.md` to understand current state
5. Consult `logos/engineering.md` for engineering constraints

---

## Current Slice / 当前切片

`current-slice.md` defines the current engineering task, scope, acceptance criteria, and authorization status.

`current-slice.md` 定义当前工程任务、范围、验收标准和授权状态。

### Key Concepts / 关键概念

- **Status:** `Proposed` / `Active` / `Completed`
- **Phase:** P1, P2, P3 (implementation phases)
- **Authorization:** A `Proposed` phase does not authorize code changes

### Before Modifying Code / 修改代码之前

1. Read `current-slice.md` to confirm the current phase status
2. If the phase is `Proposed`, do not modify code — report the required authorization
3. If the phase is `Active`, verify your changes are within the declared scope
4. If your changes require work outside the declared scope, stop and report

---

## Authority Hierarchy / 权威层次

When documents conflict, resolve in this order:

当文档冲突时，按以下顺序解决：

1. `logos/VISION.md` — Long-term direction / 长期方向
2. `logos/intent.md` — Current commitments / 当前承诺
3. `logos/decisions.md` — Accepted decisions / 已接受的决策
4. `current-slice.md` — Current task authorization / 当前任务授权
5. `logos/reality.md` — Observed state / 观察状态
6. `logos/engineering.md` — Engineering constraints / 工程约束

These are semantic roles, not a precedence ranking. A `Proposed` slice does not override an `accepted` intent.

这些是语义角色，不是优先级排序。`Proposed` 状态的切片不能覆盖 `accepted` 状态的 intent。

---

## Agent Boundary / Agent 边界

### Agent May / Agent 可以

- Read all files in `logos/` and `current-slice.md`
- Propose changes to `current-slice.md` (requires human acceptance)
- Implement code within the authorized scope of an `Active` phase
- Generate evidence (test results, execution logs)
- Update `logos/reality.md` with observed facts (with evidence)
- Report conflicts between documents

### Agent May Not / Agent 不可以

- Modify `logos/VISION.md`, `logos/intent.md`, or `logos/decisions.md` without explicit human authorization
- Treat a `Proposed` phase as authorized for implementation
- Create speculative architecture, generic frameworks, or additional documentation without justification from an active task
- Claim a phase is complete without meeting all acceptance criteria
- Silently weaken acceptance criteria to obtain a passing result
- Infer correctness beyond available evidence from code existence, passing tests, or successful execution

---

## Core Principles / 核心原则

1. **Distinguish Intent, Decision, Reality, and Evidence.**
   明确区分 Intent、Decision、Reality 与 Evidence。

2. **Unaccepted assumptions must not become normative constraints.**
   未接受的假设不得成为规范性约束。

3. **Do not infer correctness beyond available evidence.**
   不得仅凭代码存在、测试通过或执行成功，推断超出已有证据范围的正确性。

4. **Validate core hypotheses before adding architecture.**
   先验证核心假设，再增加架构和抽象。

5. **A stop condition is a valid result.**
   停止条件是有效结果。不要为了获得通过的结果而悄悄弱化验收标准。

---

## Navigation by Task / 按任务导航

| Task / 任务 | First Read / 首读 |
|------------|------------------|
| Understand project direction / 理解项目方向 | `logos/VISION.md` |
| Understand current commitments / 理解当前承诺 | `logos/intent.md` |
| Check what has been decided / 检查已决策内容 | `logos/decisions.md` |
| Understand current state / 理解当前状态 | `logos/reality.md` |
| Understand engineering constraints / 理解工程约束 | `logos/engineering.md` |
| Start implementation / 开始实现 | `current-slice.md` |
| Resolve semantic conflict / 解决语义冲突 | Stop and report / 停止并报告 |

---

## Semantic Gap / 语义缺口

When encountering unresolved semantic issues:

遇到未解决的语义问题时：

1. Stop further inference / 停止进一步推导
2. Identify the minimal human decision question / 定位最小人类决策问题
3. Wait for semantic resolution / 等待语义裁决
4. Continue engineering / 继续工程

**Do not:**
- Fill gaps with inference / 用推理填空
- Treat `candidate` as `accepted` / 把 candidate 当作 accepted
- Treat `Proposed` as authorized / 把 Proposed 当作已授权

---

## File Lock Protocol / 文件锁定协议

When a file's first line contains `<!-- AGENT-LOCKED: true -->`:

当文件首行包含 `<!-- AGENT-LOCKED: true -->` 时：

- Do not modify, delete, rename, or move the file / 不得修改、删除、重命名或移动文件
- Do not indirectly rewrite through generated files / 不得通过生成文件间接重写
- If modification is needed: stop → report → identify the locked file → wait for explicit human authorization / 如需修改：停止 → 报告 → 指出被锁文件 → 等待人类明确授权

---

## Minimal Project Rule / 最小项目规则

The current structure is minimal:

当前结构是最小的：

```
tinnery/
├── logos/           # Semantic authority / 语义权威
├── current-slice.md # Current task / 当前任务
├── AGENTS.md        # Agent instructions / Agent 指令
├── README.md        # Project introduction / 项目介绍
├── pyproject.toml   # Python package config / Python 包配置
└── tinnery/         # Core package / 核心包
```

Do not create additional directories or files unless justified by an active task.

除非有活跃任务证明其必要性，否则不要创建额外的目录或文件。
