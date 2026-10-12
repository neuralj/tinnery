# Flow Contract and Execution Boundary / Flow 契约与执行边界

> **Type / 类型:** Engineering Contract / 工程契约
> **Status / 状态:** Accepted / 已接受
> **Scope / 范围:** Tinnery Core (`tinnery/`) / Tinnery Core 包
> **Authority / 权威来源:** Implemented in commit `7526b58`; verified by 26 root tests + 13 demo tests / 在提交 `7526b58` 实现；由 26 个根测试 + 13 个演示测试验证
> **Observation / 观察时间:** 2026-10-12

---

## 1. Overview / 概述

This document describes the Flow contract and execution boundary as implemented in `tinnery/`.

本文档描述 `tinnery/` 中实现的 Flow 契约与执行边界。

### 1.1 Design Position / 设计立场

The Core implements the **smallest mechanism** that can produce checkable evidence:

Core 只实现能产出可核查证据的**最小机制**：

1. **Binding over discovery / 绑定优于发现.** A host function is bound directly to a contract. There is no
   entry-point scan, no plugin registry, no version resolution.
   宿主函数直接绑定到契约。没有 entry point 扫描、没有插件注册表、没有版本解析。

2. **Execution and verification are separate records / 执行与验证是两条独立记录.**
   A successful invocation is execution evidence, not a correctness verdict. `Executor` and `verify_output`
   are different functions producing different objects.
   调用成功是执行证据，不是正确性判决。`Executor` 与 `verify_output` 是不同函数，产出不同对象。

3. **Declared effects are not enforced effects / 声明的副作用不是被强制的副作用.**
   `FlowContract` records `declared_side_effects` and the Core sets `effects_enforced = False`.
   There is no sandbox in the current design.
   `FlowContract` 记录 `declared_side_effects`，Core 设置 `effects_enforced = False`。
   当前设计没有沙箱。

4. **Evidence is minimized / 证据最小化.**
   Receipts store digests of input and output, not the payloads themselves.
   回执只存输入与输出的摘要，不存明文。

---

## 2. Flow Contract / Flow 契约

Location: `tinnery/contract.py` / 位置：`tinnery/contract.py`

### 2.1 FlowContract / Flow 契约对象

```python
@dataclass(frozen=True)
class FlowContract:
    flow_id: str
    contract_version: str
    input_schema: dict[str, Any]      # stored as canonical JSON internally
    output_schema: dict[str, Any]     # stored as canonical JSON internally
    declared_side_effects: tuple[str, ...]
    effects_enforced: bool            # always False in this design
    contract_sha256: str
```

`FlowContract.define(...)` constructs the contract after meta-validating both schemas.

**Key-order independence / 键序无关性:**
Private schema fields store **canonical JSON strings** rather than dicts, so
`contract_sha256` is identical for two contracts written with different key orders.

私有字段存储**规范化 JSON 字符串**而非 dict，因此两个键序不同的契约得到相同的 `contract_sha256`。

### 2.2 Schema Validation / 契约校验

Validation is split into two stages:

校验分为两个阶段：

#### Stage A — Definition-time meta-validation / 定义期元校验

`_validate_schema_definition(schema, path)` validates the **schema itself**:

- `required` must be a subset of declared `properties`
- `minLength` must not exceed `maxLength`
- `array` type must declare `items`

#### Stage B — Runtime value validation / 运行期值校验

`validate_value(value, schema, path="$")` checks only values: type, length, range, and enum membership.

#### Fail-closed keyword policy / 关键字 fail-closed 策略

```python
unsupported = set(schema) - allowed
if unsupported:
    raise ContractDefinitionError(f"{path} uses unsupported schema keywords: {names}")
```

Allowed keywords are released **per type** — `properties` is accepted only for `object`, `minItems`
only for `array`. This prevents silent degradation.

**Consequence / 后果:** `$ref`, `oneOf`, `pattern`, `format` and similar keywords **raise** rather
than degrade. The validator is not a complete JSON Schema implementation.

---

## 3. Implementation Identity / 实现身份

Location: `tinnery/identity.py` / 位置：`tinnery/identity.py`

```python
@dataclass(frozen=True)
class ImplementationIdentity:
    entrypoint: str                    # "module.qualified_function"
    module_source_sha256: str          # digest of the defining source file
    callable_code_sha256: str          # digest of dis.Bytecode(fn).dis()
    dependency_manifest_sha256: str | None
    implementation_sha256: str         # canonical digest of entrypoint + source + manifest
```

### 3.1 Why three digests / 为什么需要三个摘要

| Digest / 摘要 | Captures / 捕获 |
|---|---|
| `module_source_sha256` | The whole defining module / 定义模块全文 |
| `callable_code_sha256` | Loaded bytecode, including runtime rewriting / 已加载字节码，含运行期改写 |
| `dependency_manifest_sha256` | Host-provided lock file / 宿主提供的锁文件 |

The bytecode digest exists to catch modifications invisible in source text — dynamic `exec`,
decorator rewriting.

### 3.2 Path exclusion / 排除路径

The absolute checkout path is **deliberately not part of the identity**.
The same content checked out at different paths must yield the same identity.

---

## 4. Binding and Execution / 绑定与执行

Location: `tinnery/runtime.py` / 位置：`tinnery/runtime.py`

### 4.1 Binding / 绑定

```python
def bind_flow(contract: FlowContract, implementation: Callable, dependency_manifest: Path | None = None) -> BoundFlow
```

`BoundFlow` holds the contract, the callable, the **snapshot** identity taken at bind time, and the
dependency manifest path.

### 4.2 Execution pipeline / 执行流水线

`Executor.invoke(flow, payload, invocation_id=None)` runs a linear guard chain:

```
1. canonical_json(payload)        → failure_code = input_not_json
2. validate_value(input)          → failure_code = input_contract_violation
3. identify(implementation) != bound identity
                                  → failure_code = implementation_identity_drift
                                    (or implementation_identity_unavailable)
4. status = FAILED; invoke
                                  → failure_code = implementation_exception
5. canonical_json + validate_value → failure_code = output_contract_violation
6. status = SUCCEEDED
```

### 4.3 Failure-safe by construction / 构造上失败安全

```python
status = "REJECTED"   # the INITIAL value
```

The initial status is `REJECTED`. Any path that does not complete every guard falls on the reject
side. Failure-safety is the default, not an exception handler.

### 4.4 Payload isolation / 载荷隔离

The payload is deep-copied by serialization round-trip (`canonical_json` → `json.loads`).
The business function receives a copy and cannot pollute the caller through object references.

### 4.5 Error and output discipline / 错误与输出纪律

- On any failure, `output` is forced to `None`. No partial results are ever returned.
- Exceptions record **only the type name**, never the message (`failure_type = type(exc).__name__`).
  This prevents sensitive detail from leaking into the evidence journal.

### 4.6 ExecutionReceipt / 执行回执

```python
@dataclass(frozen=True)
class ExecutionReceipt:
    receipt_version: str
    invocation_id: str
    started_at: str
    finished_at: str
    status: str              # SUCCEEDED | FAILED | REJECTED
    failure_code: str | None
    failure_type: str | None
    flow_id: str
    contract_version: str
    contract_sha256: str
    implementation_sha256: str
    entrypoint: str
    module_source_sha256: str
    callable_code_sha256: str
    dependency_manifest_sha256: str | None
    input_sha256: str | None
    output_sha256: str | None
    runtime: dict[str, str]
    execution_boundary: str
    declared_effects: tuple[str, ...]
    effects_enforced: bool
```

Receipts contain digests and status, **not payloads**. Reconstructing data from a receipt is not possible.

### 4.7 Observed failure codes / 观察到的 failure_code

| Code / 代码 | Meaning / 含义 | State / 状态 |
|---|---|---|
| `input_not_json` | Payload is not JSON-serializable / 载荷不可 JSON 序列化 | `REJECTED` |
| `input_contract_violation` | Input violates input schema / 输入违反契约 | `REJECTED` |
| `implementation_identity_drift` | Loaded code no longer matches bind-time identity / 已加载代码与绑定身份不符 | `REJECTED` |
| `implementation_identity_unavailable` | Identity could not be computed / 身份无法计算 | `REJECTED` |
| `implementation_exception` | Business function raised / 业务函数抛出异常 | `FAILED` |
| `output_contract_violation` | Output violates output schema / 输出违反契约 | `FAILED` |

---

## 5. Independent Verification / 独立验证

Location: `tinnery/verification.py` / 位置：`tinnery/verification.py`

### 5.1 Separation from execution / 与执行分离

```python
def verify_output(flow: BoundFlow, result: InvocationResult, verifier_id: str, verifier: Callable, journal: EvidenceJournal | None = None) -> VerificationRecord
```

`verify_output` does **not** modify the execution result and does not change the execution status.

### 5.2 Three gates / 三道闸门

**Gate 1 — Failed execution can never be verified.**
If `result.receipt.status != "SUCCEEDED"`, the verification status is `SKIPPED`.

**Gate 2 — Self-certification is forbidden.**

```python
if result.receipt.status == "SUCCEEDED" and verifier is flow.implementation:
    status = "REJECTED"
    failure_code = "self_verification_forbidden"
```

The comparison uses **object identity** (`is`), not digest equality.

**Gate 3 — The verifier is itself a managed object.**
The verifier's three digests are written into the `VerificationRecord`.

### 5.3 Named checks are mandatory / 必须返回具名检查项

A verifier must return a non-empty collection of **string** check names.

### 5.4 VerificationRecord / 验证记录

```python
@dataclass(frozen=True)
class VerificationRecord:
    verification_version: str
    verification_id: str
    execution_invocation_id: str
    verified_at: str
    status: str                    # PASS | FAIL | SKIPPED | REJECTED
    verifier_id: str
    verifier_implementation_sha256: str | None
    verifier_source_sha256: str | None
    verifier_code_sha256: str | None
    checked_output_sha256: str | None
    checks: tuple[str, ...]
    failure_code: str | None
    failure_type: str | None
```

---

## 6. Evidence Journal / 证据日志

Location: `tinnery/evidence.py` / 位置：`tinnery/evidence.py`

```python
class EvidenceJournal:
    def append_execution(self, receipt: ExecutionReceipt) -> None: ...
    def append_verification(self, record: VerificationRecord) -> None: ...
```

Behavior / 行为:

- Creates parent directories (`mkdir(parents=True)`)
- Opens with `newline="\n"` for cross-platform consistency
- Writes one JSON object per line (JSONL)
- Calls `flush()` then `os.fsync()`

Its own docstring states: **single-writer, not tamper-proof.**

---

## 7. Dual-Entry Invocation / 双入口调用

### 7.1 Host CLI Entry / 宿主 CLI 入口

```python
# demos/contacts_cli/contacts_cli/flows.py
from tinnery import FlowContract, bind_flow
from contacts_cli.units.normalize import normalize_contacts

CONTACTS_CONTRACT = FlowContract.define(
    flow_id="contacts.normalize",
    contract_version="1.0.0",
    input_schema={"type": "array", "items": CONTACT_SCHEMA_INPUT},
    output_schema={"type": "array", "items": CONTACT_SCHEMA_OUTPUT},
)

CONTACTS_FLOW = bind_flow(CONTACTS_CONTRACT, normalize_contacts)
```

```python
# demos/contacts_cli/contacts_cli/tasks.py
from tinnery import Executor
from contacts_cli.flows import CONTACTS_FLOW

invocation = Executor().invoke(CONTACTS_FLOW, contacts)
receipt = invocation.receipt
```

### 7.2 Dagster Entry / Dagster 入口

```python
# tinnery/dagster/ops.py
from tinnery.runtime import BoundFlow, Executor

def make_flow_op(bound_flow: BoundFlow, journal=None, name=None):
    @op(name=op_name, config_schema={"payload": Any})
    def flow_op(context):
        payload = context.op_config.get("payload")
        invocation_id = f"dagster:{context.run_id}"
        executor = Executor(journal)
        invocation = executor.invoke(bound_flow, payload, invocation_id=invocation_id)
        # ...
    return flow_op
```

### 7.3 Shared Implementation Verification / 共享实现验证

Both entries use the same `BoundFlow` object (`CONTACTS_FLOW`), which contains:
- The same `FlowContract` (same `contract_sha256`)
- The same `ImplementationIdentity` (same `implementation_sha256`, `module_source_sha256`, `callable_code_sha256`)

Tests verify:
- `test_both_entries_share_contract_digest`
- `test_both_entries_share_implementation_identity`
- `test_both_entries_produce_identical_business_output`
- `test_both_entries_use_same_bound_flow`

---

## 8. Scope Boundary / 范围边界

This contract makes **no claim** about:

- Sandboxing or isolation of candidate code / 候选代码的沙箱或隔离
- Tamper-proof evidence / 防篡改证据
- Package discovery, plugin registry, or version resolution / 包发现、插件注册表、版本解析
- Remote invocation semantics (deadline, retry, idempotency) / 远程调用语义
- Version activation, rollback, or anti-rollback / 版本激活、回滚、反回滚
- Full JSON Schema conformance / 完整 JSON Schema 一致性
- Dagster integration beyond an optional adapter / 超出可选适配器的 Dagster 集成
