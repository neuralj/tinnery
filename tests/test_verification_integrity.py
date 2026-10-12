"""Test: Output integrity verification before running verifier.

测试：运行 verifier 前的输出完整性验证。
"""

import pytest

from tinnery import FlowContract, bind_flow, Executor, verify_output


def test_modified_output_is_rejected_without_calling_verifier():
    """Modified output should cause REJECTED before verifier runs.
    
    修改的输出应该在 verifier 运行前导致 REJECTED。
    
    This test verifies Decision 3: output inconsistency verification status.
    
    本测试验证决策 3：输出不一致验证状态。
    """
    # Define a function that returns a mutable list / 定义一个返回可变列表的函数
    def func(x):
        return [{"value": x}]
    
    # Create a contract / 创建契约
    contract = FlowContract.define(
        flow_id="test.integrity",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"value": {"type": "integer"}},
                "required": ["value"],
            },
        },
    )
    
    # Bind and execute / 绑定并执行
    bound_flow = bind_flow(contract, func)
    result = Executor().invoke(bound_flow, 5)
    
    # Verify execution succeeded / 验证执行成功
    assert result.receipt.status == "SUCCEEDED"
    
    # Modify the output / 修改输出
    result.output[0]["value"] = 999
    
    # Track whether verifier was called / 追踪 verifier 是否被调用
    verifier_called = {"value": False}
    
    def verifier(output):
        verifier_called["value"] = True
        return ["check_passed"]
    
    # Run verification / 运行验证
    record = verify_output(bound_flow, result, "test-verifier", verifier)
    
    # Assertions / 断言
    # 1. Status is REJECTED / 状态为 REJECTED
    assert record.status == "REJECTED"
    
    # 2. Failure code is output_integrity_violation / 失败代码为 output_integrity_violation
    assert record.failure_code == "output_integrity_violation"
    
    # 3. Verifier was NOT called / verifier 未被调用
    assert verifier_called["value"] is False
    
    # 4. checked_output_sha256 differs from receipt's output_sha256 / checked_output_sha256 与回执的 output_sha256 不同
    assert record.checked_output_sha256 != result.receipt.output_sha256


def test_unmodified_output_is_verified_against_receipt_digest():
    """Unmodified output should pass integrity check and proceed to verification.
    
    未修改的输出应该通过完整性检查并继续进行验证。
    
    This test verifies the normal path: output matches receipt digest.
    
    本测试验证正常路径：输出与回执摘要匹配。
    """
    # Define a function / 定义一个函数
    def func(x):
        return [{"value": x}]
    
    # Create a contract / 创建契约
    contract = FlowContract.define(
        flow_id="test.integrity",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"value": {"type": "integer"}},
                "required": ["value"],
            },
        },
    )
    
    # Bind and execute / 绑定并执行
    bound_flow = bind_flow(contract, func)
    result = Executor().invoke(bound_flow, 5)
    
    # Verify execution succeeded / 验证执行成功
    assert result.receipt.status == "SUCCEEDED"
    
    # Do NOT modify the output / 不修改输出
    
    # Define a verifier / 定义一个 verifier
    def verifier(output):
        assert output == [{"value": 5}]
        return ["value_check", "structure_check"]
    
    # Run verification / 运行验证
    record = verify_output(bound_flow, result, "test-verifier", verifier)
    
    # Assertions / 断言
    # 1. Status is PASS / 状态为 PASS
    assert record.status == "PASS"
    
    # 2. Failure code is None / 失败代码为 None
    assert record.failure_code is None
    
    # 3. Checks are recorded / 检查项被记录
    assert record.checks == ("value_check", "structure_check")
    
    # 4. checked_output_sha256 matches receipt's output_sha256 / checked_output_sha256 与回执的 output_sha256 匹配
    assert record.checked_output_sha256 == result.receipt.output_sha256
