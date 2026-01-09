# -*- coding: utf-8 -*-
"""
验证模块
测试安装后的工具是否可用
"""

import subprocess
from typing import Dict, Tuple

from install_toolchain import TOOLS, MSYS2_BASH, print_info, print_success, print_error, print_warning
from tool_detection import check_tool_via_command, check_tool_via_msys2


def verify_tool(tool_key: str) -> Tuple[bool, str]:
    """
    验证工具是否可用
    返回: (是否可用, 版本信息)
    """
    tool_config = TOOLS.get(tool_key)
    if not tool_config:
        return False, "未知工具"
    
    tool_name = tool_config['name']
    check_command = tool_config.get('check_command')
    
    if not check_command:
        # 对于MSYS2，检查目录是否存在
        if tool_key == 'msys2':
            if MSYS2_BASH.exists():
                return True, "MSYS2已安装"
            else:
                return False, "MSYS2未找到"
        return False, "无检查命令"
    
    # 对于通过pacman安装的工具，优先通过MSYS2环境检查
    pacman_package = tool_config.get('pacman_package')
    if pacman_package and MSYS2_BASH.exists():
        # 先尝试MSYS2环境
        installed, version = check_tool_via_msys2(check_command, tool_name)
        if installed:
            return True, version
    
    # 再尝试系统PATH
    installed, version = check_tool_via_command(check_command, tool_name)
    if installed:
        return True, version
    
    # 如果还没找到，再尝试MSYS2环境（对于非pacman安装的工具）
    if MSYS2_BASH.exists() and not pacman_package:
        installed, version = check_tool_via_msys2(check_command, tool_name)
        if installed:
            return True, version
    
    return False, "未找到"


def verify_all_tools() -> Dict[str, Tuple[bool, str]]:
    """
    验证所有工具
    返回: {工具名: (是否可用, 版本信息)}
    """
    results = {}
    
    print_info("验证工具安装...")
    
    for tool_key in ['msys2', 'cmake', 'make', 'openocd', 'arm_gcc']:
        success, info = verify_tool(tool_key)
        results[tool_key] = (success, info)
        
        tool_name = TOOLS[tool_key]['name']
        if success:
            print_success(f"{tool_name}: {info}")
        else:
            print_error(f"{tool_name}: {info}")
    
    return results


def print_verification_summary(results: Dict[str, Tuple[bool, str]]):
    """打印验证摘要"""
    print("\n" + "="*60)
    print("验证摘要")
    print("="*60)
    
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    for tool_key, (success, info) in results.items():
        tool_name = TOOLS[tool_key]['name']
        status = "✓" if success else "✗"
        print(f"{status} {tool_name}: {info}")
    
    print(f"\n总计: {success_count}/{total_count} 工具已安装并可用")
    
    if success_count == total_count:
        print_success("所有工具验证通过！")
    else:
        print_warning(f"有 {total_count - success_count} 个工具未安装或不可用")

