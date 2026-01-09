# -*- coding: utf-8 -*-
"""
工具检测模块
检查本地是否已安装各个工具
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

from install_toolchain import MSYS2_DIR, MSYS2_BASH, TOOLS, print_info, print_success, print_warning


def check_msys2_installed() -> Tuple[bool, Optional[str]]:
    """
    检查MSYS2是否已安装
    返回: (是否安装, 版本信息或路径)
    """
    if not MSYS2_DIR.exists():
        return False, None
    
    if not MSYS2_BASH.exists():
        return False, None
    
    # 尝试获取MSYS2版本
    try:
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', 'echo $MSYSTEM'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        if result.returncode == 0:
            return True, f"MSYS2已安装在: {MSYS2_DIR}"
    except:
        pass
    
    return True, f"MSYS2目录存在: {MSYS2_DIR}"


def check_tool_via_command(command: str, tool_name: str) -> Tuple[bool, Optional[str]]:
    """
    通过命令检查工具是否可用
    返回: (是否可用, 版本信息)
    """
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0] if result.stdout else "已安装"
            return True, version
    except FileNotFoundError:
        return False, None
    except Exception as e:
        return False, None
    
    return False, None


def check_tool_via_msys2(command: str, tool_name: str) -> Tuple[bool, Optional[str]]:
    """
    通过MSYS2环境检查工具是否可用
    返回: (是否可用, 版本信息)
    """
    if not MSYS2_BASH.exists():
        return False, None
    
    try:
        # 使用mingw64环境执行命令（工具安装在mingw64/bin目录下）
        # 方法1: 直接使用mingw64/bin中的可执行文件路径
        cmd_name = command.split()[0]
        tool_path = MSYS2_DIR / "mingw64" / "bin" / f"{cmd_name}.exe"
        
        if tool_path.exists():
            # 工具文件存在，尝试执行命令
            # 设置MSYSTEM环境变量为MINGW64，这样PATH会自动包含/mingw64/bin
            env = os.environ.copy()
            env['MSYSTEM'] = 'MINGW64'
            
            result = subprocess.run(
                [str(MSYS2_BASH), '-lc', command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10,
                env=env
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0] if result.stdout else "已安装"
                return True, version
        
        # 方法2: 如果文件不存在或执行失败，尝试直接执行命令（可能已经在PATH中）
        env = os.environ.copy()
        env['MSYSTEM'] = 'MINGW64'
        env['PATH'] = str(MSYS2_DIR / "mingw64" / "bin") + os.pathsep + env.get('PATH', '')
        
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10,
            env=env
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0] if result.stdout else "已安装"
            return True, version
    except Exception as e:
        pass
    
    return False, None


def check_all_tools(force: bool = False) -> Dict[str, Tuple[bool, Optional[str]]]:
    """
    检查所有工具的安装状态
    返回: {工具名: (是否安装, 版本信息)}
    """
    results = {}
    
    # 检查MSYS2
    msys2_installed, msys2_info = check_msys2_installed()
    results['msys2'] = (msys2_installed, msys2_info)
    
    if not msys2_installed:
        # 如果MSYS2未安装，其他工具也无法通过MSYS2检查
        results['cmake'] = (False, None)
        results['make'] = (False, None)
        results['openocd'] = (False, None)
        results['arm_gcc'] = (False, None)
        return results
    
    # 检查CMake
    cmake_config = TOOLS['cmake']
    if cmake_config['check_command']:
        # 先尝试系统PATH
        installed, version = check_tool_via_command(cmake_config['check_command'], 'cmake')
        if not installed:
            # 再尝试MSYS2环境
            installed, version = check_tool_via_msys2(cmake_config['check_command'], 'cmake')
        results['cmake'] = (installed, version)
    else:
        results['cmake'] = (False, None)
    
    # 检查Make
    make_config = TOOLS['make']
    if make_config['check_command']:
        # 先尝试系统PATH
        installed, version = check_tool_via_command(make_config['check_command'], 'make')
        if not installed:
            # 再尝试MSYS2环境
            installed, version = check_tool_via_msys2(make_config['check_command'], 'make')
        results['make'] = (installed, version)
    else:
        results['make'] = (False, None)
    
    # 检查OpenOCD
    openocd_config = TOOLS['openocd']
    if openocd_config['check_command']:
        # 优先通过MSYS2环境检查（因为通过pacman安装在MSYS2中）
        installed, version = check_tool_via_msys2(openocd_config['check_command'], 'openocd')
        if not installed:
            # 再尝试系统PATH
            installed, version = check_tool_via_command(openocd_config['check_command'], 'openocd')
        results['openocd'] = (installed, version)
    else:
        results['openocd'] = (False, None)
    
    # 检查ARM GCC
    arm_gcc_config = TOOLS['arm_gcc']
    if arm_gcc_config['check_command']:
        # 优先通过MSYS2环境检查（因为通过pacman安装在MSYS2中）
        installed, version = check_tool_via_msys2(arm_gcc_config['check_command'], 'arm_gcc')
        if not installed:
            # 再尝试系统PATH
            installed, version = check_tool_via_command(arm_gcc_config['check_command'], 'arm_gcc')
        results['arm_gcc'] = (installed, version)
    else:
        results['arm_gcc'] = (False, None)
    
    return results


def print_tool_status(results: Dict[str, Tuple[bool, Optional[str]]]):
    """打印工具状态"""
    for tool_key, (installed, info) in results.items():
        tool_name = TOOLS[tool_key]['name']
        if installed:
            print_success(f"{tool_name}: {info or '已安装'}")
        else:
            print_warning(f"{tool_name}: 未安装")

