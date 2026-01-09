# -*- coding: utf-8 -*-
"""
测试脚本 - 验证工具基本功能
"""
import sys
import os

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

from tools.base import PrintUtils, WingetUtils, osversion, osarch

def test_basic():
    """测试基本功能"""
    print("=" * 60)
    print("Windows 一键安装工具 - 基础功能测试")
    print("=" * 60)
    print()

    # 测试系统信息
    PrintUtils.print_info(f"系统版本: {osversion}")
    PrintUtils.print_info(f"系统架构: {osarch}")
    PrintUtils.print_info(f"Python 版本: {sys.version.split()[0]}")
    print()

    # 测试打印工具
    PrintUtils.print_success("✓ 成功消息测试")
    PrintUtils.print_info("ℹ 信息消息测试")
    PrintUtils.print_warning("⚠ 警告消息测试")
    PrintUtils.print_error("✗ 错误消息测试")
    print()

    # 测试 winget
    PrintUtils.print_info("检查 winget 可用性...")
    if WingetUtils.check_winget():
        PrintUtils.print_success("✓ winget 可用")
    else:
        PrintUtils.print_warning("⚠ winget 不可用，某些功能可能无法使用")
    print()

    PrintUtils.print_success("=" * 60)
    PrintUtils.print_success("基础功能测试完成!")
    PrintUtils.print_success("=" * 60)

if __name__ == '__main__':
    try:
        test_basic()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
