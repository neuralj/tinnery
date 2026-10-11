# Engineering / 工程

> **Type / 类型:** Engineering projection / 工程投影
> **Status / 状态:** Descriptive / 描述性
> **Scope / 范围:** Project / 项目级
> **Authority / 权威来源:** Tinnery engineering constraints / Tinnery 工程约束

> Note: This is an engineering description, not semantic authority. System structure is constrained by Vision and Intent in logos/.
> 注意：这是工程描述，不是语义权威。系统结构受 logos/ 中的 Vision 和 Intent 约束。

---

## Current Systems / 当前系统

**Status:** No systems implemented yet / 暂无系统实现

---

## Target Architecture / 目标架构

Based on VISION.md and intent.md:
基于 VISION.md 和 intent.md：

### Core Components / 核心组件

1. **Tinnery Core Package** (`tinnery/`)
   - Flow protocol implementation / Flow 协议实现
   - Version governance / 版本治理
   - Independent verification / 独立验证

2. **Demonstration Host** (`examples/contacts_cli/`)
   - Contact normalization CLI / 联系人标准化 CLI
   - Domain logic ownership / 领域逻辑所有权
   - SQLite I/O / SQLite 读写

### Data Flow / 数据流

```
CLI Demo
    ↓
Tinnery Core (shared protocol)
    ↓
Version Resolution
    ↓
Business Implementation (V1/V2)
    ↓
Independent Verification
    ↓
Activation / Rollback
```

---

## Engineering Constraints / 工程约束

- Use Python standard library for P1 / P1 使用 Python 标准库
- Synthetic test data only / 仅使用合成测试数据
- Source data read-only / 源数据只读
- Output in disposable target / 输出在可丢弃目标中
- Transformation logic independent of database access / 转换逻辑独立于数据库访问

---

## Operational Contracts / 运行契约

（暂无）
