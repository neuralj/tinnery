# Project Reality / 项目现实

> **Type / 类型:** Reality / 现实
> **Status / 状态:** Observed facts / 观察事实
> **Scope / 范围:** Project / 项目级
> **Observed Revision / 观察版本:** 10df1d197d533b7a9fff0a5706fa1ebe2adb7c16
> **Observation Time / 观察时间:** 2026-10-12
> **Source / 来源:** Repository inspection, local test execution, GitHub Actions run / 仓库检查、本地测试执行、GitHub Actions 运行

---

## Current Repository State / 当前仓库状态

**Repository:** tinnery
**Remote:** https://github.com/neuralj/tinnery
**Language:** Python 3.14
**Status:** P2 completed: Tinnery Core Flow protocol with dual-entry (host CLI + Dagster) shared implementation / P2 完成：Tinnery Core Flow 协议，双入口（宿主 CLI + Dagster）共享实现

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
│   ├── overview.md    # Engineering models and constraints / 工程模型与约束
│   └── flow-contract.md  # P2 Flow contract specification / P2 Flow 契约规范
├── tinnery/           # Tinnery Core package / Tinnery Core 包
│   ├── __init__.py    # Public exports / 公开导出
│   ├── identity.py    # FlowIdentity, ImplementationIdentity / Flow 身份、实现身份
│   ├── invocation.py  # InvocationRequest, InvocationResult / 调用请求、调用结果
│   ├── contract.py    # FlowContract (schema + side effects) / Flow 契约
│   ├── provider.py    # Provider protocol / Provider 协议
│   ├── evidence.py    # ExecutionEvidence (SHA256, verifiable) / 执行证据
│   ├── core.py        # invoke_flow, create_invocation_request / 核心调用
│   └── dagster/       # Dagster integration (optional extra) / Dagster 集成
│       ├── __init__.py
│       ├── resources.py  # TinneryResource wrapping a Provider / 包装 Provider 的资源
│       ├── ops.py        # make_flow_op: run request → Flow invocation / 运行请求到 Flow 调用
│       └── jobs.py       # make_flow_job: single-op job / 单 op job
├── demos/
│   └── contacts_cli/  # P1 host demonstration, P2-integrated / P1 宿主演示，已集成 P2
│       ├── pyproject.toml              # UV deps; path dep on tinnery / UV 依赖；tinnery 路径依赖
│       ├── README.md
│       ├── contacts_cli/
│       │   ├── __init__.py
│       │   ├── cli.py                  # CLI layer; logs evidence / CLI 层；记录证据
│       │   ├── tasks.py                # Task layer; invokes Flow via Tinnery Core / Task 层；经 Tinnery Core 调用 Flow
│       │   ├── flows.py                # P2: FLOW_IDENTITY, IMPLEMENTATION_IDENTITY, Provider / P2 契约与 Provider
│       │   ├── config.py
│       │   └── units/                  # Business implementation (single source) / 业务实现（唯一来源）
│       │       ├── normalize.py
│       │       └── database.py
│       └── tests/                      # 13 host CLI tests / 13 个宿主 CLI 测试
├── tests/            # P2 root tests: protocol + dual-entry acceptance / P2 根测试
│   ├── conftest.py                     # Makes demo importable / 使演示可导入
│   ├── test_flow_contract.py           # Core protocol tests / 核心协议测试
│   └── test_dual_entry.py              # Dual-entry acceptance tests / 双入口验收测试
├── .github/workflows/ci.yml  # CI: root tests + demo tests / CI：根测试 + 演示测试
├── current-slice.md   # Current engineering task / 当前工程任务
├── AGENTS.md
├── README.md
├── pyproject.toml     # tinnery package; dagster/dev extras / tinnery 包；dagster/dev 可选依赖
├── uv.lock            # Root lockfile / 根锁文件
└── .gitignore
```

---

## Implementation Status / 实现状态

**Code:** P2 completed: Flow contract + dual-entry integration / P2 已完成：Flow 契约 + 双入口集成 (CURRENT)
**Tests:** 22 root tests + 13 demo tests passing locally and in CI / 22 根测试 + 13 演示测试本地与 CI 均通过 (CURRENT)
**CI:** GitHub Actions runs root and demo suites on push/PR/dispatch / GitHub Actions 在 push/PR/手动触发时运行根与演示测试 (CURRENT)
**Deployment:** Not deployed; no Dagster instance runs / 未部署；无运行中的 Dagster 实例 (CURRENT)

### P2 Implementation Details / P2 实现细节

**Shared contract (facts):**
- `FLOW_IDENTITY = contacts.normalize@1.0.0 (contract: 1.0.0)` defined in `demos/contacts_cli/contacts_cli/flows.py`
- `IMPLEMENTATION_IDENTITY` code_hash is SHA256 of the single business source file `units/normalize.py`
- `ContactsNormalizeProvider` validates Flow and implementation identity before executing

**Entries (facts):**
- Host entry: `contacts_cli run` → `process_contacts_task` → `invoke_normalize_flow` → `invoke_flow`; evidence (`trace_id`, `evidence_hash`) returned by task and logged by CLI
- Dagster entry: `make_flow_op` + `make_flow_job`; op config `inputs` maps to typed inputs; `trace_id = dagster:<run_id>`; `invoked_by = "dagster"`; output records `{invocation_result, execution_evidence}`; failed invocations fail the Dagster step with `FlowInvocationFailed`

**Evidence semantics (facts):**
- `invoke_flow` captures provider exceptions as a failure `InvocationResult` and still records `ExecutionEvidence`; callers decide whether to raise
- `ExecutionEvidence.verify_hash()` recomputes the SHA256 over the evidence payload; tampering (e.g. changed trace_id) makes verification fail (tested)

**Files created (P2):**
- `tinnery/{__init__,identity,invocation,contract,provider,evidence,core}.py`
- `tinnery/dagster/{__init__,resources,ops,jobs}.py`
- `demos/contacts_cli/contacts_cli/flows.py`
- `tests/{conftest,test_flow_contract,test_dual_entry}.py`
- `engineering/flow-contract.md`
- Root `pyproject.toml` + `uv.lock`; demo path dependency `tinnery = { path = "../..", editable = true }`

**Verified behaviors (local + CI):**
- Dual entries share identical Flow identity and implementation identity (same code_hash)
- Both entries produce identical business output for identical inputs
- Spy test: both entries reach the single `normalize_contacts` function (2 calls, 1 implementation)
- Host task records verifiable evidence; failure path raises before writing target db
- Dagster failure path fails the step with `FlowInvocationFailed`
- Dagster version 1.13.26 used for integration tests

---

## Current Slice Status / 当前切片状态

**Slice:** Shared Flow Lifecycle with a Contact CLI
**Status:** Proposed / 提案中 (CURRENT)
**Authorization:** P1 and P2 completed; P3 not authorized / P1 与 P2 已完成；P3 未授权 (CURRENT)

### Phase Status / 阶段状态

- **P1 — Host CLI Baseline:** Completed / 已完成
  - CI verified (push events); PR trigger and failure scenario not yet verified / CI 已验证（push 事件）；PR 触发与失败场景尚未验证
- **P2 — Shared Flow Protocol:** Completed / 已完成 (CURRENT)
  - All six acceptance criteria met; verified by tests and CI run 38197271229 / 六项验收标准全部满足；由测试与 CI run 38197271229 验证
- **P3 — Version Governance:** Not yet authorized / 尚未授权 (CURRENT)

---

## Goals Status / 目标状态

**G-01:** Validate the Shared Flow Lifecycle
**Status:** Candidate / 候选 (CURRENT)
**Acceptance:** Requires explicit decision after full validation / 需要完整验证后明确决策 (CURRENT)

---

## Recent Governance Changes / 近期治理变更

**D-001 (Accepted, 2026-10-12):** Use Dagster as Tinnery's Initial Operator-Facing Entry Point
D-001（已接受，2026-10-12）：采用 Dagster 作为 Tinnery 的初始操作入口

Realization: partial — P2 dual-entry integration verified via tests and CI; no Dagster UI or scheduling exercised.
实现状态：部分 — P2 双入口集成已由测试与 CI 验证；Dagster UI 与调度未实际使用。

See `logos/decisions.md` for details.
详见 `logos/decisions.md`。

---

## Unverified Claims / 未验证声明

- No runtime behavior has been verified beyond local and CI testing.
- No deployment or production use has occurred; no Dagster instance or UI has been run.
- Dagster code locations (separate processes / RPC transport) have not been exercised; only in-process `execute_in_process` execution is verified.
- P3 has not been implemented or validated.
- PR trigger and intentional-failure CI scenario remain unverified (inherited from P1).
- The target architecture described in `engineering/overview.md` remains partly proposed.

---

## Evidence / 证据

**P2 test execution (local):**
```
# Root suite (protocol + dual-entry acceptance)
uv run --locked pytest -q
22 passed in 2.63s

# Demo suite (host CLI layers, post-integration)
cd demos/contacts_cli && uv run --locked pytest -q
13 passed in 0.05s
```

**P1 test execution (local, pre-integration baseline):**
```
13 passed in 0.06s
```

**CLI execution (post-integration):**
```
$ uv run contacts-cli run input.sqlite output.sqlite
INFO: Reading contacts from source database
INFO: Read 5 contacts
INFO: Normalizing contacts through Tinnery Core
INFO: Normalized 5 contacts (trace_id=... evidence_hash=...)
INFO: Writing contacts to target database
INFO: Wrote 5 contacts
INFO: Successfully processed 5 contacts
INFO: Tinnery execution evidence: trace_id=... evidence_hash=...
```

**CI verification (cloud) — P2:**
- Run ID: 38197271229
- Status: success
- Duration: 15s
- Trigger: push to main
- Commit: 10df1d197d533b7a9fff0a5706fa1ebe2adb7c16
- Runner: ubuntu-latest (GitHub-hosted)
- Root tests: 22 passed in 2.48s
- Demo tests: 13 passed in 0.10s
- URL: https://github.com/neuralj/tinnery/actions/runs/38197271229

**CI verification (cloud) — P1:**
- Run ID: 38191275154
- Status: success
- Commit: 86afc44a0fb486af92bec1406a0ff2dff599fd08
- URL: https://github.com/neuralj/tinnery/actions/runs/38191275154

**Verified:**
- ✅ Runs on GitHub-hosted runner (not self-hosted)
- ✅ Uses minimal permissions (contents: read)
- ✅ No credentials injected
- ✅ No deployment or activation
- ✅ Both test suites pass in cloud environment with locked dependencies
- ✅ Dual entries share one Flow contract and one implementation (tested)
- ✅ Execution evidence is recorded and hash-verifiable on both entries (tested)

**Not Yet Verified / 尚未验证:**
- ❌ PR trigger: no pull_request event runs observed
- ❌ Failure scenario: no intentional failure test observed in CI
- ❌ Dagster UI, daemon, code locations, or scheduling
