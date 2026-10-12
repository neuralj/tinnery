"""Test: Bytecode change detection in implementation identity.

测试：实现身份中的字节码变化检测。
"""

import pytest

from tinnery import FlowContract, bind_flow
from tinnery.identity import identify


def test_bytecode_change_alters_full_identity_not_source_digest():
    """Modifying function __code__ should change full identity but not source digest.
    
    修改函数 __code__ 应该改变完整身份，但不改变源码级摘要。
    
    This test verifies Decision 1: implementation_sha256 is source-level identity,
    while callable_code_sha256 captures bytecode-level changes.
    
    本测试验证决策 1：implementation_sha256 是源码级身份，而 callable_code_sha256
    捕获字节码级变化。
    """
    # Define a simple function / 定义一个简单函数
    def func(x):
        return x + 1
    
    # Get baseline identity / 获取基线身份
    identity_v1 = identify(func)
    
    # Define a modified function with compatible signature / 定义一个签名兼容的修改后函数
    def modified_func(x):
        _ = None  # Change bytecode / 改变字节码
        return x + 1
    
    # Replace __code__ to simulate runtime modification / 替换 __code__ 模拟运行时修改
    func.__code__ = modified_func.__code__
    
    # Get new identity / 获取新身份
    identity_v2 = identify(func)
    
    # Assertions / 断言
    # 1. Entrypoint unchanged (same function object) / 入口点不变（同一个函数对象）
    assert identity_v1.entrypoint == identity_v2.entrypoint
    
    # 2. Source file digest unchanged (same file) / 源文件摘要不变（同一个文件）
    assert identity_v1.module_source_sha256 == identity_v2.module_source_sha256
    
    # 3. Bytecode digest changed / 字节码摘要变化
    assert identity_v1.callable_code_sha256 != identity_v2.callable_code_sha256
    
    # 4. Source-level digest unchanged (design decision) / 源码级摘要不变（设计决策）
    assert identity_v1.implementation_sha256 == identity_v2.implementation_sha256
    
    # 5. Full identity changed (runtime comparison) / 完整身份变化（运行时比较）
    assert identity_v1 != identity_v2
