"""Test: Evidence persistence semantics with and without Journal.

测试：有和没有 Journal 时的证据持久化语义。
"""

import json
import tempfile
from pathlib import Path

import pytest

from tinnery import FlowContract, bind_flow, Executor, EvidenceJournal


def test_invoke_returns_receipt_without_journal():
    """Core invocation returns receipt when Journal not configured.
    
    未配置 Journal 时，Core 调用仍返回回执。
    
    This test verifies that Executor works without a Journal and returns
    a valid receipt. Note: this does not prove absence of persistence,
    only that the Core API functions correctly without Journal.
    
    本测试验证 Executor 在没有 Journal 时仍能工作并返回有效回执。
    注意：这不能证明没有持久化，只能证明 Core API 在没有 Journal 时正常工作。
    """
    # Define a function / 定义一个函数
    def func(x):
        return x + 1
    
    # Create a contract / 创建契约
    contract = FlowContract.define(
        flow_id="test.persistence",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={"type": "integer"},
    )
    
    # Bind the function / 绑定函数
    bound_flow = bind_flow(contract, func)
    
    # Execute without Journal / 不带 Journal 执行
    executor = Executor()  # No journal parameter / 没有 journal 参数
    result = executor.invoke(bound_flow, 5)
    
    # Assertions / 断言
    # 1. Receipt is returned / 回执已返回
    assert result.receipt is not None
    
    # 2. Receipt status is SUCCEEDED / 回执状态为 SUCCEEDED
    assert result.receipt.status == "SUCCEEDED"
    
    # 3. Output is correct / 输出正确
    assert result.output == 6
    
    # 4. Receipt has expected fields / 回执有预期字段
    assert result.receipt.invocation_id
    assert result.receipt.flow_id == "test.persistence"
    assert result.receipt.contract_sha256 == contract.digest


def test_journal_persists_execution_receipt():
    """JSONL contains corresponding receipt when Journal configured.
    
    配置 Journal 时，JSONL 中出现对应回执。
    
    This test verifies that when a Journal is provided, the execution
    receipt is persisted to the JSONL file.
    
    本测试验证当提供 Journal 时，执行回执被持久化到 JSONL 文件。
    """
    # Define a function / 定义一个函数
    def func(x):
        return x + 1
    
    # Create a contract / 创建契约
    contract = FlowContract.define(
        flow_id="test.persistence",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={"type": "integer"},
    )
    
    # Bind the function / 绑定函数
    bound_flow = bind_flow(contract, func)
    
    # Create a temporary journal file / 创建临时 journal 文件
    with tempfile.TemporaryDirectory() as tmpdir:
        journal_path = Path(tmpdir) / "evidence.jsonl"
        journal = EvidenceJournal(journal_path)
        
        # Execute with Journal / 带 Journal 执行
        executor = Executor(journal)
        result = executor.invoke(bound_flow, 5)
        
        # Assertions / 断言
        # 1. Receipt is returned / 回执已返回
        assert result.receipt is not None
        assert result.receipt.status == "SUCCEEDED"
        
        # 2. Journal file exists / Journal 文件存在
        assert journal_path.exists()
        
        # 3. Journal file contains one line / Journal 文件包含一行
        lines = journal_path.read_text().strip().split("\n")
        assert len(lines) == 1
        
        # 4. Line is valid JSON / 行是有效的 JSON
        record = json.loads(lines[0])
        assert record["record_type"] == "execution_receipt"
        
        # 5. Record matches receipt / 记录与回执匹配
        assert record["record"]["invocation_id"] == result.receipt.invocation_id
        assert record["record"]["flow_id"] == "test.persistence"
        assert record["record"]["status"] == "SUCCEEDED"


def test_journal_does_not_change_execution_outcome():
    """Writing to Journal does not change business result or key identity digests.
    
    写入 Journal 不改变调用的业务结果和关键身份摘要。
    
    This test verifies that the presence of a Journal does not affect
    the execution outcome, ensuring separation of concerns between
    business execution and evidence persistence.
    
    本测试验证 Journal 的存在不影响执行结果，确保业务执行和证据持久化之间的关注点分离。
    """
    # Define a function / 定义一个函数
    def func(x):
        return x + 1
    
    # Create a contract / 创建契约
    contract = FlowContract.define(
        flow_id="test.persistence",
        contract_version="1.0",
        input_schema={"type": "integer"},
        output_schema={"type": "integer"},
    )
    
    # Bind the function / 绑定函数
    bound_flow = bind_flow(contract, func)
    
    # Execute without Journal / 不带 Journal 执行
    result_without_journal = Executor().invoke(bound_flow, 5)
    
    # Execute with Journal / 带 Journal 执行
    with tempfile.TemporaryDirectory() as tmpdir:
        journal_path = Path(tmpdir) / "evidence.jsonl"
        journal = EvidenceJournal(journal_path)
        result_with_journal = Executor(journal).invoke(bound_flow, 5)
        
        # Assertions / 断言
        # 1. Business result is the same / 业务结果相同
        assert result_without_journal.output == result_with_journal.output
        
        # 2. Receipt status is the same / 回执状态相同
        assert result_without_journal.receipt.status == result_with_journal.receipt.status
        
        # 3. Key identity digests are the same / 关键身份摘要相同
        assert result_without_journal.receipt.implementation_sha256 == result_with_journal.receipt.implementation_sha256
        assert result_without_journal.receipt.contract_sha256 == result_with_journal.receipt.contract_sha256
        
        # 4. Invocation IDs are different (different executions) / 调用 ID 不同（不同的执行）
        assert result_without_journal.receipt.invocation_id != result_with_journal.receipt.invocation_id
