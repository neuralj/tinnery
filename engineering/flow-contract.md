# Flow Contract and Execution Boundary / Flow 契约与执行边界

> **Type / 类型:** Engineering Contract / 工程契约
> **Status / 状态:** Proposed / 提议
> **Scope / 范围:** P2 implementation / P2 实施
> **Authority / 权威来源:** D-001 (Accepted) / D-001（已接受）

---

## 1. Overview / 概述

This document defines the Flow Contract and Execution Boundary for Tinnery. It specifies how Flow identity, invocation protocol, and execution evidence are structured to enable dual-entry invocation (Host CLI and Dagster) of the same business implementation.

本文档定义 Tinnery 的 Flow 契约与执行边界。它规定 Flow 身份、调用协议和执行证据的结构，以支持双入口（宿主 CLI 和 Dagster）调用相同的业务实现。

---

## 2. Flow Identity / Flow 身份

### 2.1 Flow Definition / Flow 定义

A Flow is identified by three components:

一个 Flow 由三个组件标识：

```python
@dataclass(frozen=True)
class FlowIdentity:
    flow_id: str              # Unique identifier / 唯一标识符
    version: str              # Flow version (semver) / Flow 版本（语义化版本）
    contract_version: str     # Contract version (semver) / 契约版本（语义化版本）
```

**Example / 示例:**

```python
flow_identity = FlowIdentity(
    flow_id="contacts.normalize",
    version="1.0.0",
    contract_version="1.0.0"
)
```

### 2.2 Implementation Identity / 实现身份

The actual business implementation is identified by:

实际业务实现由以下内容标识：

```python
@dataclass(frozen=True)
class ImplementationIdentity:
    implementation_id: str    # Unique identifier / 唯一标识符
    version: str              # Implementation version / 实现版本
    code_hash: str            # SHA256 hash of implementation code / 实现代码的 SHA256 哈希
    metadata: dict            # Additional metadata (author, timestamp, etc.) / 附加元数据
```

**Example / 示例:**

```python
implementation_identity = ImplementationIdentity(
    implementation_id="contacts.normalize.v1",
    version="1.0.0",
    code_hash="a1b2c3d4e5f6...",
    metadata={
        "author": "system",
        "created_at": "2026-10-12T00:00:00Z",
        "source": "demos/contacts_cli/contacts_cli/units/normalize.py"
    }
)
```

---

## 3. Invocation Protocol / 调用协议

### 3.1 Invocation Request / 调用请求

```python
@dataclass(frozen=True)
class InvocationRequest:
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    inputs: dict[str, Any]    # Typed inputs / 类型化输入
    context: dict[str, Any]   # Execution context (trace_id, etc.) / 执行上下文
```

**Example / 示例:**

```python
request = InvocationRequest(
    flow_identity=flow_identity,
    implementation_identity=implementation_identity,
    inputs={
        "contacts": [
            {"contact_id": 1, "full_name": "  Alice   Chen  ", "email": " ALICE@EXAMPLE.COM "}
        ]
    },
    context={
        "trace_id": "abc123",
        "invoked_by": "host_cli"  # or "dagster"
    }
)
```

### 3.2 Invocation Result / 调用结果

```python
@dataclass(frozen=True)
class InvocationResult:
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    outputs: dict[str, Any]   # Typed outputs / 类型化输出
    status: str               # "success" | "failure" / 状态
    error: str | None         # Error message if failed / 失败时的错误消息
    execution_metadata: dict  # Duration, resource usage, etc. / 执行元数据
```

**Example / 示例:**

```python
result = InvocationResult(
    flow_identity=flow_identity,
    implementation_identity=implementation_identity,
    outputs={
        "normalized_contacts": [
            {"contact_id": 1, "full_name": "Alice Chen", "email": "alice@example.com"}
        ]
    },
    status="success",
    error=None,
    execution_metadata={
        "duration_ms": 42,
        "records_processed": 1
    }
)
```

---

## 4. Provider Interface / Provider 接口

### 4.1 Abstract Provider / 抽象 Provider

```python
class Provider(Protocol):
    """Abstract interface for business implementation providers.
    
    业务实现提供者的抽象接口。
    """
    
    def invoke(
        self,
        request: InvocationRequest
    ) -> InvocationResult:
        """Invoke the business implementation.
        
        调用业务实现。
        """
        ...
```

### 4.2 Host Provider / 宿主 Provider

Host applications implement the Provider interface to expose their business logic:

宿主应用实现 Provider 接口以暴露其业务逻辑：

```python
class ContactsNormalizeProvider:
    """Provider for contacts.normalize Flow.
    
    contacts.normalize Flow 的 Provider。
    """
    
    def __init__(self, implementation_identity: ImplementationIdentity):
        self.implementation_identity = implementation_identity
    
    def invoke(self, request: InvocationRequest) -> InvocationResult:
        # Validate request matches expected Flow / 验证请求匹配预期 Flow
        if request.flow_identity != expected_flow_identity:
            raise ValueError("Flow identity mismatch")
        
        # Execute business logic / 执行业务逻辑
        contacts = request.inputs["contacts"]
        normalized = normalize_contacts(contacts)
        
        # Return typed result / 返回类型化结果
        return InvocationResult(
            flow_identity=request.flow_identity,
            implementation_identity=self.implementation_identity,
            outputs={"normalized_contacts": normalized},
            status="success",
            error=None,
            execution_metadata={"duration_ms": 42, "records_processed": len(contacts)}
        )
```

---

## 5. Execution Boundary / 执行边界

### 5.1 Input/Output Contract / 输入输出契约

Each Flow defines its input and output contract:

每个 Flow 定义其输入输出契约：

```python
@dataclass(frozen=True)
class FlowContract:
    flow_identity: FlowIdentity
    input_schema: dict        # JSON Schema or type definition / JSON Schema 或类型定义
    output_schema: dict       # JSON Schema or type definition / JSON Schema 或类型定义
    side_effects: list[str]   # Declared side effects / 声明的副作用
```

**Example / 示例:**

```python
contract = FlowContract(
    flow_identity=flow_identity,
    input_schema={
        "type": "object",
        "properties": {
            "contacts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "contact_id": {"type": "integer"},
                        "full_name": {"type": "string"},
                        "email": {"type": "string"}
                    },
                    "required": ["contact_id", "full_name", "email"]
                }
            }
        },
        "required": ["contacts"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "normalized_contacts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "contact_id": {"type": "integer"},
                        "full_name": {"type": "string"},
                        "email": {"type": "string"}
                    },
                    "required": ["contact_id", "full_name", "email"]
                }
            }
        },
        "required": ["normalized_contacts"]
    },
    side_effects=["none"]  # Pure transformation / 纯转换
)
```

### 5.2 Execution Constraints / 执行约束

- **Source data read-only / 源数据只读:** Providers must not modify source data
  Provider 不得修改源数据
- **Output isolation / 输出隔离:** Outputs must be written to disposable targets
  输出必须写入可丢弃目标
- **No side effects beyond declaration / 无超出声明的副作用:** Providers must not perform undeclared side effects
  Provider 不得执行未声明的副作用
- **Implementation identity preserved / 实现身份保留:** Execution evidence must record the actual implementation identity
  执行证据必须记录实际实现身份

---

## 6. Execution Evidence / 执行证据

### 6.1 Evidence Structure / 证据结构

```python
@dataclass(frozen=True)
class ExecutionEvidence:
    trace_id: str                          # Unique trace identifier / 唯一追踪标识符
    flow_identity: FlowIdentity
    implementation_identity: ImplementationIdentity
    invocation_request: InvocationRequest
    invocation_result: InvocationResult
    invoked_by: str                        # "host_cli" | "dagster" / 调用方
    timestamp: str                         # ISO 8601 / ISO 8601 时间戳
    evidence_hash: str                     # SHA256 hash of evidence / 证据的 SHA256 哈希
```

### 6.2 Evidence Requirements / 证据要求

- **Completeness / 完整性:** Evidence must include request, result, and identity
  证据必须包括请求、结果和身份
- **Verifiability / 可验证性:** Evidence hash must be computable and verifiable
  证据哈希必须可计算和验证
- **Traceability / 可追溯性:** Evidence must link to specific Flow and implementation versions
  证据必须链接到特定的 Flow 和实现版本

---

## 7. Dual-Entry Invocation / 双入口调用

### 7.1 Host CLI Entry / 宿主 CLI 入口

```python
# Host CLI invokes through Tinnery Core / 宿主 CLI 通过 Tinnery Core 调用
from tinnery import create_invocation_request, invoke_flow

request = create_invocation_request(
    flow_identity,
    implementation_identity,
    {"contacts": contacts},
    trace_id="cli-trace-001",
    invoked_by="host_cli",
)

result, evidence = invoke_flow(request, ContactsNormalizeProvider())
if not result.is_success:
    raise RuntimeError(result.error)  # caller decides / 由调用方决定
```

Provider exceptions are captured as a failure `InvocationResult` with full
execution evidence; `invoke_flow` itself does not raise. Callers (CLI task,
Dagster op) decide whether to fail their own execution.

Provider 异常被捕获为带完整执行证据的失败 `InvocationResult`；`invoke_flow`
本身不抛出。由调用方（CLI task、Dagster op）决定是否使自己的执行失败。

### 7.2 Dagster Entry / Dagster 入口

```python
# Dagster invokes through Dagster Integration / Dagster 通过 Dagster Integration 调用
from tinnery.dagster import make_flow_op, make_flow_job

flow_op = make_flow_op(flow_identity, implementation_identity, provider)
flow_job = make_flow_job(flow_op)

# Run request maps to typed inputs via op config
# 运行请求经 op config 映射为类型化输入
execution = flow_job.execute_in_process(
    run_config={"ops": {flow_op.name: {"config": {"inputs": {"contacts": contacts}}}}}
)
output = execution.output_for_node(flow_op.name)  # {invocation_result, execution_evidence}
```

The op's `trace_id` is `dagster:<run_id>` and `invoked_by` is `dagster`.
失败的调用使 Dagster step 失败并记录证据日志。op 的 `trace_id` 为
`dagster:<run_id>`，`invoked_by` 为 `dagster`。

### 7.3 Shared Implementation Verification / 共享实现验证

Both entries must:

两个入口必须：

1. Use the same FlowIdentity / 使用相同的 FlowIdentity
2. Use the same ImplementationIdentity / 使用相同的 ImplementationIdentity
3. Record execution evidence with the same structure / 记录相同结构的执行证据
4. Not duplicate business logic / 不重复业务逻辑

---

## 8. P2 Acceptance Criteria / P2 验收标准

P2 is complete when:

P2 完成时：

- [ ] FlowContract, FlowIdentity, ImplementationIdentity are defined
  FlowContract、FlowIdentity、ImplementationIdentity 已定义
- [ ] InvocationRequest, InvocationResult are defined
  InvocationRequest、InvocationResult 已定义
- [ ] Provider interface is defined
  Provider 接口已定义
- [ ] Host CLI invokes business implementation through Tinnery Core
  宿主 CLI 通过 Tinnery Core 调用业务实现
- [ ] Dagster invokes the same implementation through Dagster Integration
  Dagster 通过 Dagster Integration 调用相同的实现
- [ ] Execution evidence is recorded for both entries
  两个入口都记录执行证据
- [ ] Verification tests prove no duplicate business implementation
  验证测试证明没有重复业务实现

---

## 9. Out of Scope / 范围外

The following are explicitly out of scope for P2:

以下内容明确不在 P2 范围内：

- Version registry or candidate activation / 版本注册表或候选激活
- Rollback mechanisms / 回滚机制
- Plugin frameworks (Entry Points, Pluggy, Stevedore) / 插件框架
- Generic scheduler or workflow UI / 通用调度器或工作流 UI
- Production deployment / 生产部署
