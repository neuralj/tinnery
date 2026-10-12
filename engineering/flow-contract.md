# Flow Contract and Execution Boundary / Flow 契约与执行边界

> **Type / 类型:** Engineering Contract / 工程契约
> **Status / 状态:** Proposed / 提议
> **Scope / 范围:** Tinnery Core (`tinnery/`) / Tinnery Core 包
> **Authority / 权威来源:** Observed implementation in the working tree; not an accepted Decision / 依据工作树中的实际实现；非已接受决策
> **Observation / 观察时间:** 2026-10-12

---

## 1. Overview / 概述

This document describes the Flow contract and execution boundary as currently implemented in `tinnery/`.
It is a **descriptive** document: every statement below is checkable against the source, and §7 lists
the places where the implementation is known to be wrong.

本文档描述 `tinnery/` 中当前实现的 Flow 契约与执行边界。这是**描述性**文档：下文每一条陈述都可对照源码核实，§7 列出已知实现缺陷。

### 1.1 Design Position / 设计立场

The Core deliberately implements the **smallest mechanism** that can produce checkable evidence:

Core 刻意只实现能产出可核查证据的**最小机制**：

1. **Binding over discovery / 绑定优于发现.** A host function is bound directly to a contract. There is no
   entry-point scan, no plugin registry, no version resolution. Package-level discovery is explicitly deferred.
   宿主函数直接绑定到契约。没有 entry point 扫描、没有插件注册表、没有版本解析。包级发现被显式推迟。

2. **Execution and verification are separate records / 执行与验证是两条独立记录.**
   A successful invocation is execution evidence, not a correctness verdict. `Executor` and `verify_output`
   are different functions producing different objects.
   调用成功是执行证据，不是正确性判决。`Executor` 与 `verify_output` 是不同函数，产出不同对象。

3. **Declared effects are not enforced effects / 声明的副作用不是被强制的副作用.**
   `FlowContract` records `declared_side_effects` and the Core sets `effects_enforced = False`.
   There is no sandbox in the current design. This must not be described as isolation.
   `FlowContract` 记录 `declared_side_effects`，Core 设置 `effects_enforced = False`。
   当前设计没有沙箱，不得将其描述为隔离。

4. **Evidence is minimized / 证据最小化.**
   Receipts store digests of input and output, not the payloads themselves.
   Receipt 只存输入与输出的摘要，不存明文。

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
Private schema fields store **canonical JSON strings** rather than dicts (`contract.py:172-173`), so
`contract_sha256` is identical for two contracts written with different key orders.

私有字段存储**规范化 JSON 字符串**而非 dict，因此两个键序不同的契约得到相同的 `contract_sha256`。

### 2.2 Schema Validation / 契约校验

Validation is deliberately split into two stages. This separation is the most important structural
choice in the module.

校验刻意分为两个阶段。这是本模块最重要的结构选择。

#### Stage A — Definition-time meta-validation / 定义期元校验

`_validate_schema_definition(schema, path)` (`contract.py:45`) validates the **schema itself**:

`_validate_schema_definition` 校验 **schema 本身**：

- `required` must be a subset of declared `properties`
- `minLength` must not exceed `maxLength`
- `array` type must declare `items`

#### Stage B — Runtime value validation / 运行期值校验

`validate_value(value, schema, path="$")` (`contract.py:114`) checks only values: type, length,
range, and enum membership.

`validate_value` 只检查值的类型、长度、范围与枚举成员。

#### Fail-closed keyword policy / 关键字 fail-closed 策略

```python
unsupported = set(schema) - allowed
if unsupported:
    raise ContractDefinitionError(f"{path} uses unsupported schema keywords: {names}")
```
(`contract.py:58-61`)

Allowed keywords are released **per type** — `properties` is accepted only for `object`, `minItems`
only for `array`. This prevents the most insidious failure mode: writing `{"pattern": "^a"}`,
having it silently ignored, and believing validation is happening.

允许的关键字**按类型放行**——`properties` 只对 `object` 放行，`minItems` 只对 `array` 放行。
这防止了最隐蔽的失败：写下 `{"pattern": "^a"}`，被静默忽略，却以为在校验。

**Consequence / 后果:** `$ref`, `oneOf`, `pattern`, `format` and similar keywords **raise** rather
than degrade. The validator is not a complete JSON Schema implementation.

`$ref`、`oneOf`、`pattern`、`format` 等关键字会**抛错**而非降级。本校验器不是完整的 JSON Schema 实现。

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
    implementation_sha256: str         # see §7.2 — excludes callable_code_sha256
```

### 3.1 Why three digests / 为什么需要三个摘要

| Digest / 摘要 | Captures / 捕获 | Source |
|---|---|---|
| `module_source_sha256` | The whole defining module / 定义模块全文 | `inspect.getsource` |
| `callable_code_sha256` | Loaded bytecode, including runtime rewriting / 已加载字节码，含运行期改写 | `dis.Bytecode(fn).dis()` |
| `dependency_manifest_sha256` | Host-provided lock file / 宿主提供的锁文件 | optional argument |

The bytecode digest exists to catch modifications invisible in source text — dynamic `exec`,
decorator rewriting. Source digest alone would miss these.

字节码摘要用于捕获源码文本中不可见的改动——动态 `exec`、装饰器改写。仅有源码摘要会漏掉这些。

### 3.2 Path exclusion / 排除路径

The absolute checkout path is **deliberately not part of the identity** (`identity.py:39-41`).
The same content checked out at different paths must yield the same identity, otherwise deployment
location would masquerade as a different implementation.

绝对 checkout 路径**刻意不计入身份**。相同内容在不同路径检出必须得到相同身份，否则部署位置会伪装成不同实现。

Runtime details (Python version, platform) are recorded separately in the receipt, because they can
still affect behavior without being part of the implementation fingerprint.

运行时信息（Python 版本、平台）单独记录在 receipt 中——它们可能影响行为，但不属于实现指纹。

---

## 4. Binding and Execution / 绑定与执行

Location: `tinnery/runtime.py` / 位置：`tinnery/runtime.py`

### 4.1 Binding / 绑定

```python
def bind_flow(contract: FlowContract, implementation: Callable, dependency_manifest: Path | None = None) -> BoundFlow
```

`BoundFlow` holds the contract, the callable, the **snapshot** identity taken at bind time, and the
dependency manifest path.

`BoundFlow` 保存契约、可调用对象、**绑定时刻的快照身份**，以及依赖清单路径。

### 4.2 Execution pipeline / 执行流水线

`Executor.invoke(flow, payload, invocation_id=None)` runs a linear guard chain:

`Executor.invoke` 运行一条线性守卫链：

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
status = "REJECTED"   # runtime.py:92 — the INITIAL value
```

The initial status is `REJECTED`. Any path that does not complete every guard falls on the reject
side. Failure-safety is the default, not an exception handler.

状态的初始值是 `REJECTED`。任何未走完守卫的路径都落在拒绝侧。失败安全是默认状态，而非异常处理。

### 4.4 Payload isolation / 载荷隔离

The payload is deep-copied by serialization round-trip (`canonical_json` → `json.loads`).
The business function receives a copy and cannot pollute the caller through object references.

载荷通过序列化往返实现深拷贝。业务函数拿到副本，无法通过对象引用污染调用方。

### 4.5 Error and output discipline / 错误与输出纪律

- On any failure, `output` is forced to `None` (`runtime.py:174`). No partial results are ever returned.
  任何失败下 `output` 强制为 `None`，绝不返回半成品。
- Exceptions record **only the type name**, never the message (`failure_type = type(exc).__name__`).
  This prevents sensitive detail from leaking into the evidence journal.
  异常只记录类型名，绝不记录消息，防止敏感细节泄漏进证据日志。

### 4.6 ExecutionReceipt / 执行回执

```python
@dataclass(frozen=True)
class ExecutionReceipt:
    receipt_version: str
    invocation_id: str
    started_at: str
    finished_at: str
    contract: dict
    identity: dict
    input_sha256: str
    output_sha256: str | None
    python_version: str
    platform: str
    status: str              # SUCCEEDED | FAILED | REJECTED
    failure_code: str | None
    failure_type: str | None
```

Receipts contain digests and status, **not payloads**. Reconstructing data from a receipt is not possible.

回执只含摘要与状态，**不含载荷**。无法从回执还原数据。

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
def verify_output(flow: BoundFlow, result: InvocationResult, verifier: Callable) -> VerificationRecord
```

`verify_output` does **not** modify the execution result and does not change the execution status.
A separate function producing a separate record.

`verify_output` **不修改**执行结果，**不改变**执行状态。独立函数产出独立记录。

### 5.2 Three gates / 三道闸门

**Gate 1 — Failed execution can never be verified.**
If `result.receipt.status != "SUCCEEDED"`, the verification status is `SKIPPED`.
A failure can never be verified into a PASS.

执行未成功时验证恒为 `SKIPPED`。失败永远不可能被验证成 PASS。

**Gate 2 — Self-certification is forbidden.**

```python
if result.receipt.status == "SUCCEEDED" and verifier is flow.implementation:
    status = "REJECTED"
    failure_code = "self_verification_forbidden"
```
(`verification.py:65-67`)

The comparison uses **object identity** (`is`), not digest equality. Two wrappers around the same
code are still distinguishable when they are the same object, and a function cannot certify itself by
re-deriving its own hash.

比较使用**对象身份**（`is`）而非摘要相等。函数无法通过重算自身哈希来给自己背书。

**Gate 3 — The verifier is itself a managed object.**
The verifier's three digests are written into the `VerificationRecord`. The verifier is not a trusted
assumption; it is a governed artifact.

验证器自身的三个摘要被写入 `VerificationRecord`。验证器不是可信假设，而是受管对象。

### 5.3 Named checks are mandatory / 必须返回具名检查项

A verifier must return a non-empty collection of **string** check names. Returning empty or non-string
values raises `ValueError` (`verification.py:72-73`).

This closes the path of "run an assert, return True, call it verified".

这堵住了「跑个 assert 然后返回 True 就当验证过了」这条路。

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

### 5.5 What this does not prove / 这不能证明什么

Code cannot establish that two distinct verifiers are organizationally independent, nor that their
business expectations are correct. `VerificationRecord(status="PASS")` means "a separately identified
verifier reported these named checks as passing" — nothing stronger.

代码无法证明两个不同的验证器在组织职责上真正独立，也无法证明其业务预期正确。
`VerificationRecord(status="PASS")` 的含义是「一个独立标识的验证器报告这些具名检查通过」，仅此而已。

---

## 6. Evidence Journal / 证据日志

Location: `tinnery/evidence.py` / 位置：`tinnery/evidence.py`

```python
class EvidenceJournal:
    def append(self, record: dict) -> None: ...
```

Behavior / 行为:

- Creates parent directories (`mkdir(parents=True)`)
- Opens with `newline="\n"` for cross-platform consistency
- Writes one JSON object per line (JSONL)
- Calls `flush()` then `os.fsync()`

Its own docstring states: **single-writer, not tamper-proof.** There is no hash chain, no signature,
no remote witness, no retention policy, no multi-writer guarantee. Anyone with write access can modify
or truncate the file.

其 docstring 明示：**单写者，不防篡改**。没有哈希链、没有签名、没有远程见证、没有保留策略、没有多写者保证。任何有写权限的人都可以修改或截断。

---

## 7. Known Implementation Defects / 已知实现缺陷

Both defects originate in `copy/tinnery-minimal-v0.1/` and are present verbatim in the current `tinnery/` package.

两处缺陷均源自 `copy/tinnery-minimal-v0.1/`，并原样存在于当前 `tinnery/` 包中。

### 7.1 Receipt records the wrong identity / 回执记录了错误的身份

**Location:** `tinnery/runtime.py:114` vs `:144`

```python
# :114  — drift detection compares against a FRESHLY computed identity
current_identity = identify(flow.implementation, flow.dependency_manifest)
if current_identity != flow.identity:
    failure_code = "implementation_identity_drift"
...
# :144  — the receipt is written with the BIND-TIME SNAPSHOT
identity = flow.identity
```

The check evaluates identity **A** (freshly computed); the receipt records identity **B** (bind-time
snapshot). Under hot reload, monkeypatching, or bytecode rewriting between check and execution, the
drift check does not fire and the receipt does not describe what actually ran.

检测用的是**新算的身份 A**，写入回执用的是**绑定时的快照 B**。在检查与执行之间代码被改动时，漂移检测不会触发，回执记录的身份也不是真正执行的那个。

**Impact / 影响:** The receipt's identity field cannot be trusted as evidence of what executed.
回执的身份字段不能作为「执行了什么」的证据。

**Fix / 修正方向:** Write `current_identity` into the receipt. (Not applied — outside authorized scope.)

### 7.2 Implementation fingerprint omits bytecode / 实现指纹漏掉字节码

**Location:** `tinnery/identity.py:64-69`

```python
source_identity = {
    "entrypoint": entrypoint,
    "module_source_sha256": source_digest,
    "dependency_manifest_sha256": dependency_digest,
}
implementation_digest = sha256(canonical_json(source_identity))
```

`callable_code_sha256` **is not an input to `implementation_sha256`**. Drift detection remains correct
because it compares the whole dataclass, but the "implementation fingerprint" concept misses the
bytecode layer. Any future registry check keyed on `implementation_sha256` would not detect a
bytecode-level replacement within the same source file.

`callable_code_sha256` **不是 `implementation_sha256` 的输入**。漂移检测仍然正确（它比较整个 dataclass），但「实现指纹」这个概念漏掉了字节码层。将来若用 `implementation_sha256` 做注册表校验，无法发现同一源文件内的字节码级替换。

**Fix / 修正方向:** Include `callable_code_sha256` in the digest input. (Not applied — outside authorized scope.)

---

## 8. Test Coverage Status / 测试覆盖状态

**Observed / 观察所得:** The repository's `tests/` directory contains only `conftest.py`. The 10 pytest
cases that exercise this contract live in `copy/tinnery-minimal-v0.1/tests/test_tinnery.py` and have
**not** been executed against the repository package.

仓库 `tests/` 目录仅有 `conftest.py`。验证本契约的 10 个 pytest 用例位于 `copy/tinnery-minimal-v0.1/tests/test_tinnery.py`，
**尚未**针对仓库包执行。

The design invariants this contract relies on, and where each is anchored:

本契约依赖的设计不变量及其对应位置：

| Invariant / 不变量 | Anchored in / 位置 |
|---|---|
| Key-order-independent contract digest / 契约摘要键序无关 | `copy/.../tests/test_tinnery.py:41` |
| Stable identity across two bindings / 两次绑定身份稳定 | `copy/.../tests/test_tinnery.py:47` |
| Input violation rejects before business function runs / 输入违规时不调用业务函数 | `copy/.../tests/test_tinnery.py:77` |
| Output violation is not success / 输出违规不算成功 | `copy/.../tests/test_tinnery.py:92` |
| Exception message absent from receipt / 回执不含异常消息 | `copy/.../tests/test_tinnery.py:103` |
| Failed execution cannot be PASS / 失败执行不能 PASS | `copy/.../tests/test_tinnery.py:113` |
| No self-certification / 禁止自我认证 | `copy/.../tests/test_tinnery.py:122` |
| Fail-closed on unsupported keyword / 未实现关键字 fail-closed | `copy/.../tests/test_tinnery.py:129` |
| Invalid contact produces no output / 无效联系人不产生输出 | `copy/.../tests/test_tinnery.py:134` |

**Until these are ported into `tests/` and executed against `tinnery/`, the behaviors described in this
document are inherited claims, not repository-verified behavior.**

**在这些用例被移植进 `tests/` 并针对 `tinnery/` 执行之前，本文档描述的行为是继承来的声明，而非仓库已验证的行为。**

---

## 9. Scope Boundary / 范围边界

This contract makes **no claim** about:

本契约**不主张**：

- Sandboxing or isolation of candidate code / 候选代码的沙箱或隔离
- Tamper-proof evidence / 防篡改证据
- Package discovery, plugin registry, or version resolution / 包发现、插件注册表、版本解析
- Remote invocation semantics (deadline, retry, idempotency) / 远程调用语义
- Version activation, rollback, or anti-rollback / 版本激活、回滚、反回滚
- Full JSON Schema conformance / 完整 JSON Schema 一致性
- Dagster integration beyond an optional adapter / 超出可选适配器的 Dagster 集成
