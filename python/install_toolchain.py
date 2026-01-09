#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入式开发工具链一键安装脚本
支持安装：MSYS2, ARM GCC, CMake, OpenOCD
"""

import os
import sys
import argparse
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 检查是否为Windows平台
if platform.system() != 'Windows':
    print("错误: 此脚本仅支持Windows平台")
    sys.exit(1)

# 脚本运行目录
SCRIPT_DIR = Path(__file__).parent.absolute()
MSYS2_DIR = SCRIPT_DIR / "msys2"
MSYS2_BASH = MSYS2_DIR / "usr" / "bin" / "bash.exe"

# 工具配置
TOOLS = {
    'msys2': {
        'name': 'MSYS2',
        'check_command': None,  # 通过目录检查
        'pacman_package': None,
    },
    'cmake': {
        'name': 'CMake',
        'check_command': 'cmake --version',
        'pacman_package': 'cmake',
    },
    'make': {
        'name': 'Make',
        'check_command': 'make --version',
        'pacman_package': 'make',
    },
    'openocd': {
        'name': 'OpenOCD',
        'check_command': 'openocd --version',
        'pacman_package': 'mingw-w64-x86_64-openocd',
    },
    'arm_gcc': {
        'name': 'ARM GCC (arm-none-eabi)',
        'check_command': 'arm-none-eabi-gcc --version',
        'pacman_package': None,  # 可能不可用
    }
}


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_info(msg: str):
    """打印信息"""
    print(f"{Colors.OKCYAN}[信息]{Colors.ENDC} {msg}")


def print_success(msg: str):
    """打印成功信息"""
    print(f"{Colors.OKGREEN}[成功]{Colors.ENDC} {msg}")


def print_warning(msg: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}[警告]{Colors.ENDC} {msg}")


def print_error(msg: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}[错误]{Colors.ENDC} {msg}")


def print_header(msg: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{msg}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def check_admin() -> bool:
    """检查是否以管理员权限运行"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='嵌入式开发工具链一键安装脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python install_toolchain.py --preview    # 预览模式
  python install_toolchain.py              # 真实安装模式
  python install_toolchain.py --skip-env   # 跳过环境变量配置
  python install_toolchain.py --force      # 强制重新安装
        """
    )
    parser.add_argument('--preview', action='store_true',
                        help='预览模式：显示安装计划但不执行实际安装')
    parser.add_argument('--skip-env', action='store_true',
                        help='跳过环境变量配置')
    parser.add_argument('--force', action='store_true',
                        help='强制重新安装（即使已存在）')
    
    args = parser.parse_args()
    
    print_header("嵌入式开发工具链安装脚本")
    
    if args.preview:
        print_info("运行在预览模式")
        from preview import run_preview_mode
        run_preview_mode(args)
    else:
        print_info("运行在真实安装模式")
        from installer import run_install_mode
        run_install_mode(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n用户中断安装")
        sys.exit(1)
    except Exception as e:
        print_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

