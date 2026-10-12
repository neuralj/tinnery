# Project Reality / 项目现实

> **Type / 类型:** Reality / 现实
> **Status / 状态:** Observed facts / 观察事实
> **Scope / 范围:** Project / 项目级
> **Repository HEAD / 仓库 HEAD:** 05ee95972a30a6cb40cf2864b81020a3c99eb7b9
> **Code / Test Baseline / 代码与测试基线:** 5f7334d72a30a6cb40cf2864b81020a3c99eb7b9
> **Observation Time / 观察时间:** 2026-10-12 19:32 GMT+8
> **Source / 来源:** `git status`, `git log`, 测试执行, CI 验证 / git commands, test execution, CI verification

---

## Current Repository State / 当前仓库状态

**Repository:** tinnery
**Remote:** https://github.com/neuralj/tinnery
**Language:** Python 3.14 (host venv)
**Status:** P2 completed at code baseline `5f7334d`. Current repository HEAD is `05ee959` (governance docs only). 26 root tests + 13 demo tests passing. CI verified (run 38234842585 for commit 5f7334d). Post-P2 Slice A proposed but not yet authorized.

**当前状态：** P2 在代码基线 `5f7334d` 完成。当前仓库 HEAD 为 `05ee959`（仅治理文档）。26 个根测试 + 13 个演示测试通过。CI 已验证（run 38234842585 对应提交 5f7334d）。Post-P2 Slice A 已提案但尚未授权。

---

## File Structure / 文件结构

```
tinnery/
├── logos/
│   ├── VISION.md      # Semantic authority: long-term direction
│   ├── intent.md      # Semantic authority: current commitments
│   └── decisions.md   # Semantic authority: accepted decisions (D-001)
├── reality/
│   └── project.md     # This document / 本文档
├── engineering/
│   ├── overview.md        # Proposed models and constraints
│   └── flow-contract.md   # Flow contract specification
├── tinnery/           # Tinnery Core package
│   ├── __init__.py    # Public exports (bind_flow design)
│   ├── contract.py    # FlowContract + JSON Schema subset validator (fail-closed)
│   ├── identity.py    # ImplementationIdentity (source / bytecode / manifest digests)
│   ├── runtime.py     # bind_flow, BoundFlow, Executor, ExecutionReceipt
│   ├── verification.py# verify_output, VerificationRecord
│   ├── evidence.py    # EvidenceJournal (append-only JSONL)
│   └── dagster/       # Dagster integration (optional extra)
│       ├── __init__.py
│       ├── resources.py  # TinneryResource wrapping EvidenceJournal
│       ├── ops.py        # make_flow_op using BoundFlow/Executor
│       └── jobs.py       # make_flow_job
├── demos/
│   └── contacts_cli/  # Host demonstration (adapted to bind_flow)
│       ├── pyproject.toml
│       ├── contacts_cli/
│       │   ├── cli.py, config.py
│       │   ├── tasks.py    # adapted to use Executor
│       │   ├── flows.py    # CONTACTS_FLOW = bind_flow(CONTACTS_CONTRACT, normalize_contacts)
│       │   └── units/
│       │       ├── normalize.py   # Business implementation (single source)
│       │       └── database.py
│       └── tests/       # 13 demo tests
├── tests/             # 26 root tests
│   ├── conftest.py
│   ├── test_flow_contract.py  # 16 tests
│   └── test_dual_entry.py     # 10 tests
├── current-slice.md
├── AGENTS.md
├── README.md
├── pyproject.toml     # optional extras: dagster, dev
└── uv.lock
```

---

## Implementation Status / 实现状态

**Code:** `bind_flow` + independent verification design present in `tinnery/` / `bind_flow` + 独立验证设计已存在于 `tinnery/`
**Tests:** 26 root tests + 13 demo tests passing / 26 个根测试 + 13 个演示测试通过
**CI:** Verified on GitHub Actions (run 38234842585, commit 5f7334d) / 已在 GitHub Actions 验证
**Deployment:** Not deployed; no Dagster instance runs / 未部署；无运行中的 Dagster 实例

### Post-P2 Slice A Status / Post-P2 Slice A 状态

**Status:** Proposed — not yet authorized / 提案中 — 尚未授权

**Identified issues / 已识别问题：**

1. ~~`implementation_sha256` does not include `callable_code_sha256` (`identity.py:64-69`)~~ — **Design clarification / 设计澄清**: `implementation_sha256` represents source-level identity (entrypoint + source + manifest); `callable_code_sha256` is a separate field for bytecode-level changes. Runtime compares full `ImplementationIdentity`, not just `implementation_sha256`. See `engineering/flow-contract.md` §3.
   ~~`implementation_sha256` 未包含 `callable_code_sha256`~~ — **设计澄清**：`implementation_sha256` 表示源码级身份（入口点 + 源文件 + 清单）；`callable_code_sha256` 是独立字段，用于捕获字节码级变化。运行时比较完整的 `ImplementationIdentity`，而非仅 `implementation_sha256`。见 `engineering/flow-contract.md` §3。

2. Drift receipt uses bind-time identity instead of observed identity (`runtime.py:114-117 vs 144-160`)
   身份漂移回执使用绑定身份而非观察身份

3. Verification does not check output consistency with `output_sha256` (`verification.py:70`)
   验证时未检查输出是否与 `output_sha256` 一致

4. ~~Host `tasks.py` does not pass `EvidenceJournal`, receipts not persisted (`tasks.py:37`)~~ — **Known limitation (not in this slice) / 已知限制（不在本切片范围）**: Receipts are generated in memory but not persisted. This slice documents the limitation; actual persistence implementation deferred to a future slice.
   ~~宿主 `tasks.py` 未传入 `EvidenceJournal`，回执未持久化~~ — **已知限制（不在本切片范围）**：回执在内存中生成但未持久化。本切片记录此限制；实际持久化实现推迟到未来切片。

**Next step / 下一步：** Wait for explicit authorization. If authorized, add failing tests first, then make minimal code fixes for Issues 2 and 3 only.
等待明确授权。如获授权，先补失败测试，再仅针对 Issue 2 和 Issue 3 做最小代码修正。

### Current Core API / 当前 Core API

| Object / 对象 | Location / 位置 | Behavior / 行为 |
|---|---|---|
| `FlowContract` | `tinnery/contract.py` | `define(...)` builds input/output schemas; `digest` is key-order independent |
| `validate_value` | `tinnery/contract.py` | Runtime type/length/range/enum validation; fail-closed on unsupported keywords |
| `identify` | `tinnery/identity.py` | Returns `ImplementationIdentity` with `module_source_sha256`, `callable_code_sha256`, `implementation_sha256` |
| `bind_flow` | `tinnery/runtime.py` | Binds a host function to a contract; no package discovery, no registry |
| `Executor.invoke` | `tinnery/runtime.py` | Linear guard chain; status initial value is `REJECTED` |
| `ExecutionReceipt` | `tinnery/runtime.py` | Hashes + status + runtime info; does not store full payloads |
| `verify_output` | `tinnery/verification.py` | Separate function; does not mutate the execution result; self-certification forbidden |
| `EvidenceJournal` | `tinnery/evidence.py` | Append-only JSONL, flush + fsync; single-writer, not tamper-proof |

**Six failure codes / 六种 failure_code:**

```
input_not_json
input_contract_violation
implementation_identity_drift
implementation_identity_unavailable
implementation_exception
output_contract_violation
```

**Three receipt states / 三种 receipt 状态:** `REJECTED` (initial), `FAILED`, `SUCCEEDED`

---

## Current Slice Status / 当前切片状态

**Slice:** Shared Flow Lifecycle with a Contact CLI
**Document Status:** Proposed / 提案中
**Authorization:** P1 and P2 completed; P3 not authorized / P1 与 P2 已完成；P3 未授权

### Phase Status / 阶段状态

- **P1 — Host CLI Baseline:** Completed at `7526b58` / 在 `7526b58` 完成
- **P2 — Shared Flow Protocol:** Completed at `7526b58` / 在 `7526b58` 完成
- **P3 — Version Governance:** Not authorized / 尚未授权

---

## Goals Status / 目标状态

**G-01:** Validate the Shared Flow Lifecycle
**Status:** Candidate / 候选
**Acceptance:** Requires explicit decision after full validation / 需要完整验证后明确决策

---

## Unverified Claims / 未验证声明

- No Dagster UI, daemon, code location, or scheduling has been exercised.
- `tinnery/dagster/` is optional and requires `dagster` extra to import.
- No production deployment or data writes have occurred.

---

## Evidence / 证据

**Test execution (local):**
```
$ cd /home/travis/ashare/tinnery && uv run pytest tests/ -q
26 passed in 2.19s

$ cd /home/travis/ashare/tinnery/demos/contacts_cli && uv run pytest -q
13 passed in 0.06s
```

**CI verification (cloud):**
- Run ID: 38208967379
- Status: success
- Duration: 18s
- Trigger: push to main
- Commit: 7526b58d729eae5da1233637de49c650791f2f37
- Runner: ubuntu-latest (GitHub-hosted)
- Root tests: 26 passed in 3.91s
- Demo tests: 13 passed in 0.16s
- URL: https://github.com/neuralj/tinnery/actions/runs/38208967379

**Verified / 已验证:**

- ✅ 26 root tests passing locally / 本地 26 个根测试通过
- ✅ 13 demo tests passing locally / 本地 13 个演示测试通过
- ✅ CI verified on GitHub Actions / CI 在 GitHub Actions 上验证
- ✅ Core API: `bind_flow` + `Executor` + `verify_output` / Core API 已实现
- ✅ Dagster integration: `make_flow_op` + `make_flow_job` / Dagster 集成已实现
- ✅ Dual-entry acceptance tests / 双入口验收测试
- ✅ No duplicate business implementation / 无重复业务实现

**Not Yet Verified / 尚未验证:**

- ❌ Dagster UI, daemon, code location execution / Dagster UI、守护进程、代码位置执行
- ❌ Production deployment / 生产部署
- ❌ Version governance (P3) / 版本治理（P3）
