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

## Governance Domains / 治理领域

Tinnery's documentation is organized into four distinct semantic roles. These are not a precedence ranking; they serve different purposes and have different authority.

Tinnery 的文档组织为四个不同的语义角色。这些不是优先级排序；它们服务于不同目的，具有不同权威。

### 1. LOGOS — Semantic Authority / 语义权威

`logos/` contains the project's semantic authority. These files define what Tinnery is, what it commits to, and what has been decided.

`logos/` 包含项目的语义权威。这些文件定义了 Tinnery 是什么、承诺做什么、以及已做出的决策。

| File / 文件 | Purpose / 用途 | When to Read / 何时阅读 |
|------------|---------------|------------------------|
| `logos/VISION.md` | Long-term direction (Why) / 长期方向（为什么） | Before any design or review / 任何设计或审查之前 |
| `logos/intent.md` | Current commitments (Will) / 当前承诺（意愿） | Before implementation / 实现之前 |
| `logos/decisions.md` | Accepted decisions / 已接受的决策 | Before making architectural choices / 做架构选择之前 |

### 2. REALITY — Observed Facts / 观察事实

`reality/` describes what exists or has been observed, with evidence.

`reality/` 描述已存在或已观察到的内容，附带证据。

| File / 文件 | Purpose / 用途 | When to Read / 何时阅读 |
|------------|---------------|------------------------|
| `reality/project.md` | Current observed state / 当前观察状态 | Before claiming what exists / 声称某物存在之前 |

### 3. ENGINEERING — Scoped Contracts and Models / 工程契约与模型

`engineering/` contains engineering constraints and proposed models. Only explicitly accepted decisions have normative force.

`engineering/` 包含工程约束和提议的模型。只有明确接受的决策才具有规范效力。

| File / 文件 | Purpose / 用途 | When to Read / 何时阅读 |
|------------|---------------|------------------------|
| `engineering/overview.md` | Proposed models and constraints / 提议的模型与约束 | Before implementation / 实现之前 |

### 4. CHANGES — History (when needed) / 变更记录（需要时）

Historical changes and verification evidence. Not created until needed.

历史变更和验证证据。在需要之前不创建。

---

## Reading Order / 阅读顺序

1. `logos/VISION.md` — Understand long-term direction / 理解长期方向
2. `logos/intent.md` — Understand current commitments / 理解当前承诺
3. `logos/decisions.md` — Check accepted decisions / 检查已接受决策
4. `reality/project.md` — Understand current observed state / 理解当前观察状态
5. `engineering/overview.md` — Review proposed models and constraints / 审查提议的模型与约束
6. `current-slice.md` — Determine active task and authorization / 确定活跃任务与授权

The reading order is navigation guidance, not a precedence ranking.

阅读顺序是导航指导，不是优先级排序。

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

## Authorization / 授权

- `Proposed` does not authorize code modification.
  `Proposed` 不授权代码修改。

- A phase marked as authorized grants permission only within its declared scope.
  标记为已授权的阶段仅在其声明范围内授予权限。

- P1 authorization does not authorize P2 or P3.
  P1 授权不授权 P2 或 P3。

- Agent instructions cannot accept a project Goal or Decision on behalf of the project.
  Agent 指令不能代表项目接受项目目标或决策。

---

## Agent Boundary / Agent 边界

### Agent May / Agent 可以

- Read all files in `logos/`, `reality/`, `engineering/`, and `current-slice.md`
- Propose changes to `current-slice.md` (requires human acceptance)
- Implement code within the authorized scope of an `Active` phase
- Generate evidence (test results, execution logs)
- Update `reality/project.md` with observed facts (with evidence)
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
| Check accepted decisions / 检查已接受决策 | `logos/decisions.md` |
| Understand current state / 理解当前状态 | `reality/project.md` |
| Review engineering models / 审查工程模型 | `engineering/overview.md` |
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
├── reality/         # Observed facts / 观察事实
├── engineering/     # Engineering models / 工程模型
├── current-slice.md # Current task / 当前任务
├── AGENTS.md        # Agent instructions / Agent 指令
├── README.md        # Project introduction / 项目介绍
├── pyproject.toml   # Python package config / Python 包配置
└── tinnery/         # Core package / 核心包
```

Do not create additional directories or files unless justified by an active task.

除非有活跃任务证明其必要性，否则不要创建额外的目录或文件。
