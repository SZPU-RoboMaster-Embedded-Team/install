# -*- coding: utf-8 -*-
"""
预览模式
显示安装计划但不执行实际安装
"""

from pathlib import Path
from typing import Dict, Tuple

from install_toolchain import (
    SCRIPT_DIR, MSYS2_DIR, TOOLS, 
    print_info, print_success, print_warning, print_header, Colors
)
from tool_detection import check_all_tools
from downloader import get_latest_msys2_url


def run_preview_mode(args):
    """运行预览模式"""
    print_header("预览模式 - 安装计划")
    
    # 检查当前状态
    print_info("检查当前安装状态...")
    tool_status = check_all_tools(force=args.force)
    
    print("\n" + "="*60)
    print("当前状态")
    print("="*60)
    for tool_key, (installed, info) in tool_status.items():
        tool_name = TOOLS[tool_key]['name']
        status = "✓ 已安装" if installed else "✗ 未安装"
        print(f"{status:12} {tool_name:25} {info or ''}")
    
    print("\n" + "="*60)
    print("安装计划")
    print("="*60)
    
    # MSYS2
    print(f"\n{Colors.BOLD}1. MSYS2{Colors.ENDC}")
    msys2_installed, _ = tool_status['msys2']
    if msys2_installed and not args.force:
        print_info("  MSYS2已安装，将跳过")
    else:
        print_info(f"  安装位置: {MSYS2_DIR}")
        msys2_url = get_latest_msys2_url()
        if msys2_url:
            print_info(f"  下载URL: {msys2_url}")
        else:
            print_warning("  无法获取下载URL")
    
    # CMake和Make
    print(f"\n{Colors.BOLD}2. CMake和Make{Colors.ENDC}")
    cmake_installed, _ = tool_status['cmake']
    make_installed = False
    if 'make' in tool_status:
        make_installed, _ = tool_status['make']
    
    if cmake_installed and make_installed and not args.force:
        print_info("  CMake和Make已安装，将跳过")
    else:
        if not msys2_installed:
            print_warning("  需要先安装MSYS2")
        print_info("  安装方式: 通过MSYS2的pacman安装")
        print_info(f"  命令: pacman -S {TOOLS['cmake']['pacman_package']} {TOOLS['make']['pacman_package']}")
        print_info(f"  安装位置: {MSYS2_DIR}/usr/bin/cmake.exe, {MSYS2_DIR}/usr/bin/make.exe")
    
    # OpenOCD
    print(f"\n{Colors.BOLD}3. OpenOCD{Colors.ENDC}")
    openocd_installed, _ = tool_status['openocd']
    if openocd_installed and not args.force:
        print_info("  OpenOCD已安装，将跳过")
    else:
        if not msys2_installed:
            print_warning("  需要先安装MSYS2")
        print_info("  安装方式: 通过MSYS2的pacman安装")
        print_info(f"  命令: pacman -S {TOOLS['openocd']['pacman_package']}")
        print_info(f"  安装位置: {MSYS2_DIR}/usr/bin/openocd.exe")
    
    # ARM GCC
    print(f"\n{Colors.BOLD}5. ARM GCC (arm-none-eabi){Colors.ENDC}")
    arm_gcc_installed, _ = tool_status['arm_gcc']
    if arm_gcc_installed and not args.force:
        print_info("  ARM GCC已安装，将跳过")
    else:
        if not msys2_installed:
            print_warning("  需要先安装MSYS2")
        print_info("  安装方式: 通过MSYS2的pacman安装")
        print_info("  命令: pacman -S mingw-w64-x86_64-arm-none-eabi-gcc")
        print_info(f"  安装位置: {MSYS2_DIR}/mingw64/bin/arm-none-eabi-gcc.exe")
    
    # 环境变量
    print(f"\n{Colors.BOLD}6. 环境变量配置{Colors.ENDC}")
    if args.skip_env:
        print_warning("  将跳过环境变量配置（--skip-env）")
    else:
        from env_config import get_msys2_paths
        paths = get_msys2_paths()
        if paths:
            print_info("  将添加以下路径到PATH:")
            for path in paths:
                print_info(f"    - {path}")
        else:
            print_info("  暂无路径需要添加")
    
    # 验证
    print(f"\n{Colors.BOLD}7. 安装后验证{Colors.ENDC}")
    print_info("  将测试所有工具是否可用")
    
    print("\n" + "="*60)
    print("注意事项")
    print("="*60)
    print_warning("1. MSYS2安装可能需要较长时间（10-30分钟）")
    print_warning("2. 环境变量配置需要管理员权限")
    print_warning("3. 配置环境变量后需要重新打开命令行窗口")
    print_warning("4. ARM GCC可能需要手动下载（如果pacman不可用）")
    
    print("\n" + "="*60)
    print("开始安装")
    print("="*60)
    print_info("运行以下命令开始真实安装:")
    cmd = "python install_toolchain.py"
    if args.force:
        cmd += " --force"
    if args.skip_env:
        cmd += " --skip-env"
    print(f"  {cmd}")

