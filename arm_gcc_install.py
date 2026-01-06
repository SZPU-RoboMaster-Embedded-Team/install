# -*- coding: utf-8 -*-
"""
ARM GCC安装模块
通过pacman安装ARM GCC工具链
"""

import os
import subprocess
from pathlib import Path
from typing import Tuple

from install_toolchain import MSYS2_DIR, MSYS2_BASH, TOOLS, print_info, print_success, print_error, print_warning
from msys2_setup import run_msys2_command


def install_arm_gcc_via_pacman() -> Tuple[bool, str]:
    """
    通过pacman安装ARM GCC
    返回: (是否成功, 信息)
    """
    if not MSYS2_BASH.exists():
        return False, "MSYS2未安装"
    
    # 直接使用mingw-w64-x86_64-arm-none-eabi-gcc包名
    package_name = 'mingw-w64-x86_64-arm-none-eabi-gcc'
    
    try:
        # 先检查包是否已安装
        print_info(f"检查 {package_name} 是否已安装...")
        check_success, stdout, stderr = run_msys2_command(
            f'pacman -Q {package_name}',
            timeout=30
        )
        
        if check_success and stdout.strip():
            print_success(f"{package_name} 已安装: {stdout.strip()}")
            return True, stdout.strip()
        
        # 如果未安装，则进行安装
        print_info(f"通过pacman安装 {package_name}...")
        install_success, install_output, install_error = run_msys2_command(
            f'pacman -S --noconfirm {package_name}',
            timeout=600
        )
        
        if install_success:
            print_success(f"通过pacman成功安装 {package_name}")
            return True, install_output
        else:
            print_error(f"pacman安装 {package_name} 失败: {install_error}")
            return False, install_error
            
    except Exception as e:
        print_error(f"安装 {package_name} 时出错: {e}")
        return False, str(e)


def install_arm_gcc() -> bool:
    """
    安装ARM GCC工具链
    通过pacman安装
    返回: 是否成功
    """
    print_info("通过pacman安装ARM GCC...")
    success, info = install_arm_gcc_via_pacman()
    
    if success:
        return True
    else:
        print_error(f"ARM GCC安装失败: {info}")
        return False

