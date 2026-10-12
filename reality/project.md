# Project Reality / 项目现实

> **Type / 类型:** Reality / 现实
> **Status / 状态:** Observed facts / 观察事实
> **Scope / 范围:** Project / 项目级
> **Observed Revision / 观察版本:** 0fd25b9
> **Observation Time / 观察时间:** 2026-10-12
> **Source / 来源:** Repository inspection / 仓库检查

---

## Current Repository State / 当前仓库状态

**Repository:** tinnery
**Remote:** https://github.com/neuralj/tinnery
**Language:** Python 3.14
**Status:** P1 implementation completed with CLI → Task → Unit architecture / P1 实现完成，采用 CLI → Task → Unit 架构

---

## File Structure / 文件结构

```
tinnery/
├── logos/
│   ├── VISION.md      # Semantic authority: long-term direction / 语义权威：长期方向
│   ├── intent.md      # Semantic authority: current commitments / 语义权威：当前承诺
│   └── decisions.md   # Semantic authority: accepted decisions / 语义权威：已接受决策
├── reality/
│   └── project.md     # Observed facts / 观察事实
├── engineering/
│   └── overview.md    # Engineering models and constraints / 工程模型与约束
├── contacts_cli/      # P1 demonstration / P1 演示
│   ├── pyproject.toml              # UV dependency management / UV 依赖管理
│   ├── README.md                   # Usage instructions / 使用说明
│   ├── contacts_cli/
│   │   ├── __init__.py
│   │   ├── cli.py                  # CLI layer (Trigger) / CLI 层（触发器）
│   │   ├── tasks.py                # Task layer (Orchestrator) / Task 层（编排器）
│   │   ├── config.py               # Configuration management / 配置管理
│   │   └── units/
│   │       ├── __init__.py
│   │       ├── normalize.py        # Unit: Contact normalization / Unit：联系人标准化
│   │       └── database.py         # Unit: Database operations / Unit：数据库操作
│   └── tests/
│       ├── conftest.py             # Pytest configuration / Pytest 配置
│       ├── test_cli.py             # CLI layer tests / CLI 层测试
│       ├── test_tasks.py           # Task layer tests / Task 层测试
│       └── test_units.py           # Unit layer tests / Unit 层测试
├── current-slice.md   # Current engineering task / 当前工程任务
├── AGENTS.md          # Agent instructions / Agent 工作规则
├── README.md          # Project introduction / 项目介绍
├── pyproject.toml     # Python package config / Python 包配置
├── tinnery/
│   └── __init__.py    # Package entry / 包入口
└── .gitignore         # Git ignore rules / Git 忽略规则
```

---

## Implementation Status / 实现状态

**Code:** P1 completed with CLI → Task → Unit architecture / P1 已完成，采用 CLI → Task → Unit 架构 (CURRENT)
**Tests:** 13 tests passing / 13 个测试通过 (CURRENT)
**Deployment:** Not deployed / 未部署 (CURRENT)

### P1 Implementation Details / P1 实现细节

**Architecture:**
- **CLI Layer** (`cli.py`): Receives external input, constructs execution requests, handles errors uniformly
- **Task Layer** (`tasks.py`): Orchestrates the complete use case, coordinates multiple units
- **Unit Layer** (`units/`): Provides stable capability boundaries, hides internal implementation

**Files created:**
- `contacts_cli/cli.py`: CLI layer using typer (68 lines)
- `contacts_cli/tasks.py`: Task layer orchestrator (43 lines)
- `contacts_cli/units/normalize.py`: Contact normalization unit (73 lines)
- `contacts_cli/units/database.py`: Database operations unit (67 lines)
- `contacts_cli/config.py`: Configuration management (5 lines)
- `tests/test_cli.py`: CLI layer tests (65 lines)
- `tests/test_tasks.py`: Task layer tests (73 lines)
- `tests/test_units.py`: Unit layer tests (108 lines)

**Test coverage:**
- CLI layer: 3 tests
- Task layer: 2 tests
- Unit layer: 8 tests
- Total: 13 tests, all passing

**Verified behaviors:**
- Whitespace trimming and collapsing / 空格修剪和合并
- Email case normalization / 邮箱大小写标准化
- Null/empty rejection / 空值拒绝
- Batch validation / 批量验证
- Failure atomicity / 失败原子性
- Idempotent operations / 幂等操作
- CLI → Task → Unit call chain / CLI → Task → Unit 调用链
- Logger unified creation / Logger 统一创建
- Error propagation / 错误传播

**Dependencies:**
- Runtime: typer >= 0.12.0
- Dev: pytest >= 8.0.0
- Package manager: UV

---

## Current Slice Status / 当前切片状态

**Slice:** Shared Flow Lifecycle with a Contact CLI
**Status:** Proposed / 提案中 (CURRENT)
**Authorization:** P1 authorized and completed / P1 已授权并完成 (CURRENT)

### Phase Status / 阶段状态

- **P1 — Host CLI Baseline:** Completed / 已完成 (CURRENT)
- **P2 — Shared Flow Protocol:** Not yet authorized / 尚未授权 (CURRENT)
- **P3 — Version Governance:** Not yet authorized / 尚未授权 (CURRENT)

---

## Goals Status / 目标状态

**G-01:** Validate the Shared Flow Lifecycle
**Status:** Candidate / 候选 (CURRENT)
**Acceptance:** Requires explicit decision after full validation / 需要完整验证后明确决策 (CURRENT)

---

## Unverified Claims / 未验证声明

- No runtime behavior has been verified beyond local testing.
- No deployment or production use has occurred.
- P2 and P3 have not been implemented or validated.
- The target architecture described in `engineering/overview.md` is proposed, not fully implemented.

---

## Evidence / 证据

**Test execution:**
```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
collected 13 items

tests/test_cli.py::TestCLI::test_cli_run_command PASSED                  [  7%]
tests/test_cli.py::TestCLI::test_cli_run_missing_source PASSED           [ 15%]
tests/test_cli.py::TestCLI::test_cli_create_sample_command PASSED        [ 23%]
tests/test_tasks.py::TestProcessContactsTask::test_process_contacts_success PASSED [ 30%]
tests/test_tasks.py::TestProcessContactsTask::test_process_contacts_fails_on_invalid_input PASSED [ 38%]
tests/test_units.py::TestNormalizeUnit::test_normalize_valid_contact PASSED [ 46%]
tests/test_units.py::TestNormalizeUnit::test_normalize_collapses_whitespace PASSED [ 53%]
tests/test_units.py::TestNormalizeUnit::test_normalize_rejects_null_name PASSED [ 61%]
tests/test_units.py::TestNormalizeUnit::test_normalize_rejects_empty_name PASSED [ 69%]
tests/test_units.py::TestNormalizeUnit::test_normalize_batch_valid_contacts PASSED [ 76%]
tests/test_units.py::TestNormalizeUnit::test_normalize_batch_fails_on_invalid_contact PASSED [ 84%]
tests/test_units.py::TestDatabaseUnit::test_read_contacts_from_source PASSED [ 92%]
tests/test_units.py::TestDatabaseUnit::test_write_contacts_to_target PASSED [100%]

============================== 13 passed in 0.09s ==============================
```

**CLI execution:**
```
$ uv run contacts-cli create-sample input.sqlite
INFO: Created sample database: input.sqlite
INFO: Inserted 5 contacts

$ uv run contacts-cli run input.sqlite output.sqlite
INFO: Reading contacts from source database
INFO: Read 5 contacts
INFO: Normalizing contacts
INFO: Normalized 5 contacts
INFO: Writing contacts to target database
INFO: Wrote 5 contacts
INFO: Successfully processed 5 contacts
```

**Output verification:**
```
(1, 'Alice Chen', 'alice@example.com')      # Whitespace and case normalized
(2, 'Bob Smith', 'bob@example.com')         # Email case normalized
(3, 'Charlie Brown', 'charlie@example.com') # Whitespace trimmed
(4, 'Diana Prince', 'diana@example.com')    # Multiple spaces collapsed
(5, 'Eve Adams', 'eve@example.com')         # Email case normalized
```
