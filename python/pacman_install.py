# -*- coding: utf-8 -*-
"""
通过pacman安装CMake和OpenOCD的模块
"""

import subprocess
from typing import Tuple, List

from install_toolchain import MSYS2_BASH, TOOLS, print_info, print_success, print_error, print_warning
from msys2_setup import run_msys2_command


def install_package_via_pacman(package_name: str, tool_name: str) -> Tuple[bool, str]:
    """
    通过pacman安装包
    返回: (是否成功, 输出信息)
    """
    if not MSYS2_BASH.exists():
        return False, "MSYS2未安装"
    
    try:
        print_info(f"通过pacman安装 {tool_name} ({package_name})...")
        
        # 先检查包是否已安装
        success, stdout, stderr = run_msys2_command(
            f'pacman -Q {package_name}',
            timeout=30
        )
        
        if success and stdout.strip():
            print_success(f"{tool_name} 已安装: {stdout.strip()}")
            return True, stdout.strip()
        
        # 安装包
        command = f'pacman -S --noconfirm {package_name}'
        success, stdout, stderr = run_msys2_command(command, timeout=600)
        
        if success:
            print_success(f"{tool_name} 安装完成")
            return True, stdout
        else:
            print_error(f"{tool_name} 安装失败: {stderr}")
            return False, stderr
            
    except Exception as e:
        print_error(f"安装 {tool_name} 时发生错误: {e}")
        return False, str(e)


def install_cmake() -> bool:
    """安装CMake和Make（一起安装）"""
    cmake_package = TOOLS['cmake']['pacman_package']
    make_package = TOOLS['make']['pacman_package']
    
    if not cmake_package or not make_package:
        print_error("CMake或Make没有配置pacman包名")
        return False
    
    # 使用批量安装函数，同时安装cmake和make
    return install_packages([cmake_package, make_package])


def install_openocd() -> bool:
    """安装OpenOCD"""
    package_name = TOOLS['openocd']['pacman_package']
    tool_name = TOOLS['openocd']['name']
    
    if not package_name:
        print_error(f"{tool_name} 没有配置pacman包名")
        return False
    
    success, _ = install_package_via_pacman(package_name, tool_name)
    return success


def install_packages(package_names: List[str]) -> bool:
    """
    批量安装多个包
    返回: 是否全部成功
    """
    if not MSYS2_BASH.exists():
        print_error("MSYS2未安装")
        return False
    
    try:
        print_info(f"批量安装包: {', '.join(package_names)}...")
        
        # 检查哪些包已安装
        packages_to_install = []
        for pkg in package_names:
            success, stdout, _ = run_msys2_command(f'pacman -Q {pkg}', timeout=30)
            if not success or not stdout.strip():
                packages_to_install.append(pkg)
            else:
                print_info(f"{pkg} 已安装: {stdout.strip()}")
        
        if not packages_to_install:
            print_success("所有包都已安装")
            return True
        
        # 安装未安装的包
        command = f'pacman -S --noconfirm {" ".join(packages_to_install)}'
        success, stdout, stderr = run_msys2_command(command, timeout=600)
        
        if success:
            print_success(f"包安装完成: {', '.join(packages_to_install)}")
            return True
        else:
            print_error(f"包安装失败: {stderr}")
            return False
            
    except Exception as e:
        print_error(f"批量安装包时发生错误: {e}")
        return False

