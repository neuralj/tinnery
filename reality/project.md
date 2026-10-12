# Project Reality / 项目现实

> **Type / 类型:** Reality / 现实
> **Status / 状态:** Observed facts / 观察事实
> **Scope / 范围:** Project / 项目级
> **Observed Revision / 观察版本:** 342e027
> **Observation Time / 观察时间:** 2026-10-12
> **Source / 来源:** Repository inspection / 仓库检查

---

## Current Repository State / 当前仓库状态

**Repository:** tinnery
**Remote:** https://github.com/neuralj/tinnery
**Language:** Python 3.14
**Status:** P1 implementation completed / P1 实现完成

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
├── examples/
│   └── contacts_cli/  # P1 demonstration / P1 演示
│       ├── __init__.py
│       ├── normalize.py      # Pure transformation logic / 纯转换逻辑
│       ├── db.py             # SQLite operations / SQLite 操作
│       ├── cli.py            # CLI entry point / CLI 入口
│       ├── create_sample_db.py  # Sample data generator / 示例数据生成
│       └── tests/
│           ├── __init__.py
│           ├── test_normalize.py      # Unit tests / 单元测试
│           └── test_integration.py    # Integration tests / 集成测试
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

**Code:** P1 completed (examples/contacts_cli/) / P1 已完成 (CURRENT)
**Tests:** 20 tests passing / 20 个测试通过 (CURRENT)
**Deployment:** Not deployed / 未部署 (CURRENT)

### P1 Implementation Details / P1 实现细节

**Files created:**
- `examples/contacts_cli/normalize.py`: Pure transformation logic (108 lines)
- `examples/contacts_cli/db.py`: SQLite read/write operations (115 lines)
- `examples/contacts_cli/cli.py`: CLI entry point (43 lines)
- `examples/contacts_cli/create_sample_db.py`: Sample data generator (52 lines)
- `examples/contacts_cli/tests/test_normalize.py`: Unit tests (142 lines)
- `examples/contacts_cli/tests/test_integration.py`: Integration tests (208 lines)

**Test coverage:**
- Normalization logic: 10 unit tests
- Database operations: 3 tests
- Full pipeline: 4 integration tests
- Total: 20 tests, all passing

**Verified behaviors:**
- Whitespace trimming and collapsing / 空格修剪和合并
- Email case normalization / 邮箱大小写标准化
- Null/empty rejection / 空值拒绝
- Batch validation / 批量验证
- Failure atomicity / 失败原子性
- Idempotent operations / 幂等操作

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
Ran 20 tests in 0.048s
OK
```

**CLI execution:**
```
$ python3 -m examples.contacts_cli.create_sample_db input.sqlite
Created sample database: input.sqlite
Inserted 5 contacts

$ python3 -m examples.contacts_cli.cli input.sqlite output.sqlite
Success: Processed 5 contacts
  Source: input.sqlite
  Target: output.sqlite
  Written: 5 contacts
```

**Output verification:**
```
(1, 'Alice Chen', 'alice@example.com')
(2, 'Bob Smith', 'bob@example.com')
(3, 'Charlie Brown', 'charlie@example.com')
(4, 'Diana Prince', 'diana@example.com')
(5, 'Eve Adams', 'eve@example.com')
```
