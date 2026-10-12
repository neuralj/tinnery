"""Test: Identity drift detection and rejection in Executor.

测试：Executor 中的身份漂移检测和拒绝。
"""

import pytest

from tinnery import FlowContract, bind_flow, Executor


# Module-level counter to avoid closure issues / 模块级计数器避免闭包问题
_call_count = 0


def test_identity_drift_is_rejected_before_invocation():
    """Identity drift after binding should cause rejection before business execution.
    
    绑定后的身份漂移应该在业务执行前导致拒绝。
    
    This test verifies that when implementation identity changes after binding,
    the Executor rejects the invocation and does not execute the business function.
    
    本测试验证当实现身份在绑定后发生变化时，Executor 拒绝调用且不执行业务函数。
    """
    global _call_count
    _call_count = 0
    
    # Define a simple function / 定义一个简单函数
    def func(x):
        return x + 1
    
    # Create a simple contract / 创建一个简单契约
    contract = FlowContract.define(
        flow_id="test.drift",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={"type": "integer"},
    )
    
    # Bind the function / 绑定函数
    bound_flow = bind_flow(contract, func)
    
    # Define a modified function (no closures, compatible signature) / 定义修改后的函数（无闭包，兼容签名）
    def modified_func(x):
        global _call_count
        _call_count += 1
        return x + 2
    
    # Replace __code__ to simulate drift / 替换 __code__ 模拟漂移
    func.__code__ = modified_func.__code__
    
    # Execute / 执行
    result = Executor().invoke(bound_flow, 5)
    
    # Assertions / 断言
    # 1. Status is REJECTED / 状态为 REJECTED
    assert result.receipt.status == "REJECTED"
    
    # 2. Failure code is implementation_identity_drift / 失败代码为 implementation_identity_drift
    assert result.receipt.failure_code == "implementation_identity_drift"
    
    # 3. Business function was NOT called / 业务函数未被调用
    assert _call_count == 0
    
    # 4. Output is None / 输出为 None
    assert result.output is None


def test_receipt_records_bind_time_and_observed_identity():
    """Drift receipt should record both bind-time and observed identities.
    
    漂移回执应该同时记录绑定身份和观测身份。
    
    This test verifies Decision 2: drift receipt field semantics.
    
    本测试验证决策 2：漂移回执字段语义。
    """
    # Define a simple function / 定义一个简单函数
    def func(x):
        return x + 1
    
    # Create a simple contract / 创建一个简单契约
    contract = FlowContract.define(
        flow_id="test.drift",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={"type": "integer"},
    )
    
    # Bind the function / 绑定函数
    bound_flow = bind_flow(contract, func)
    bind_time_identity = bound_flow.identity
    
    # Modify function to simulate drift / 修改函数模拟漂移
    def modified_func(x):
        _ = None
        return x + 2
    
    func.__code__ = modified_func.__code__
    
    # Execute / 执行
    result = Executor().invoke(bound_flow, 5)
    
    # Assertions / 断言
    # 1. Receipt has bind_time_identity / 回执有 bind_time_identity
    assert hasattr(result.receipt, 'bind_time_identity')
    assert result.receipt.bind_time_identity == bind_time_identity
    
    # 2. Receipt has observed_identity / 回执有 observed_identity
    assert hasattr(result.receipt, 'observed_identity')
    assert result.receipt.observed_identity is not None
    
    # 3. Observed identity differs from bind-time / 观测身份与绑定时不同
    assert result.receipt.observed_identity != bind_time_identity
    
    # 4. Observed identity has different bytecode digest / 观测身份有不同的字节码摘要
    assert result.receipt.observed_identity.callable_code_sha256 != bind_time_identity.callable_code_sha256
    
    # 5. Receipt version is "2" / 回执版本为 "2"
    assert result.receipt.receipt_version == "2"
