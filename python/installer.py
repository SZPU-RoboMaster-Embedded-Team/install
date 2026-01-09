# -*- coding: utf-8 -*-
"""
安装器主模块
执行实际的安装流程
"""

import os
import sys
from pathlib import Path
from typing import Optional

from install_toolchain import (
    SCRIPT_DIR, MSYS2_DIR, print_info, print_success, print_error, 
    print_warning, print_header, check_admin
)
from tool_detection import check_all_tools, print_tool_status
from downloader import download_msys2
from msys2_setup import (
    install_msys2_from_exe, install_msys2_from_archive, 
    initialize_msys2, check_msys2_ready
)
from pacman_install import install_cmake, install_openocd
from arm_gcc_install import install_arm_gcc
from env_config import configure_environment_variables
from verification import verify_all_tools, print_verification_summary


def run_install_mode(args):
    """运行真实安装模式"""
    print_header("开始安装")
    
    # 检查管理员权限
    if not args.skip_env and not check_admin():
        print_warning("未以管理员身份运行，环境变量将添加到用户PATH")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print_info("安装已取消")
            return
    
    # 检查当前状态
    print_info("检查当前安装状态...")
    tool_status = check_all_tools(force=args.force)
    print_tool_status(tool_status)
    
    # 1. 安装MSYS2
    print_header("步骤 1/7: 安装MSYS2")
    msys2_installed, _ = tool_status['msys2']
    
    # 检查是否已有msys64目录（MSYS2可能已解压但未移动到msys2）
    msys64_dir = SCRIPT_DIR / "msys64"
    if not msys2_installed and msys64_dir.exists() and (msys64_dir / "usr" / "bin" / "bash.exe").exists():
        print_info("发现已解压的MSYS2（msys64目录），将移动到msys2目录...")
        import shutil
        try:
            if MSYS2_DIR.exists():
                shutil.rmtree(MSYS2_DIR)
            shutil.move(str(msys64_dir), str(MSYS2_DIR))
            print_success("MSYS2已移动到目标位置")
            msys2_installed = True
        except Exception as e:
            print_error(f"移动MSYS2目录失败: {e}")
            print_warning("将尝试重新安装")
            msys2_installed = False
    
    if msys2_installed and not args.force:
        print_success("MSYS2已安装，跳过")
    else:
        if args.force and msys2_installed:
            print_warning("强制重新安装，将删除现有MSYS2")
            import shutil
            if MSYS2_DIR.exists():
                try:
                    shutil.rmtree(MSYS2_DIR)
                    print_success("已删除现有MSYS2")
                except Exception as e:
                    print_error(f"删除现有MSYS2失败: {e}")
                    return
        
        # 检查是否已有msys64目录
        if msys64_dir.exists() and (msys64_dir / "usr" / "bin" / "bash.exe").exists():
            print_info("发现已解压的MSYS2（msys64目录），将移动到msys2目录...")
            import shutil
            try:
                if MSYS2_DIR.exists():
                    shutil.rmtree(MSYS2_DIR)
                shutil.move(str(msys64_dir), str(MSYS2_DIR))
                print_success("MSYS2已移动到目标位置")
            except Exception as e:
                print_error(f"移动MSYS2目录失败: {e}")
                print_warning("将尝试重新下载和安装")
                # 继续执行下载和安装流程
        else:
            # 下载MSYS2
            print_info("下载MSYS2安装包...")
            success, installer_path = download_msys2(SCRIPT_DIR, force=args.force)
            
            if not success or not installer_path:
                print_error("MSYS2下载失败")
                return
            
            # 安装MSYS2
            if installer_path.suffix == '.exe':
                # exe安装程序
                if not install_msys2_from_exe(installer_path, MSYS2_DIR):
                    print_error("MSYS2安装失败")
                    return
            else:
                # 归档文件
                if not install_msys2_from_archive(installer_path, MSYS2_DIR):
                    print_error("MSYS2安装失败")
                    return
    
    # 2. 初始化MSYS2
    print_header("步骤 2/7: 初始化MSYS2")
    if not check_msys2_ready():
        print_info("初始化MSYS2环境...")
        if not initialize_msys2():
            print_error("MSYS2初始化失败")
            return
    else:
        print_success("MSYS2已就绪")
    
    # 3. 安装CMake和Make
    print_header("步骤 3/7: 安装CMake和Make")
    cmake_installed, cmake_info = tool_status['cmake']
    make_installed = False
    make_info = None
    if 'make' in tool_status:
        make_installed, make_info = tool_status['make']
    
    if cmake_installed and make_installed and not args.force:
        cmake_version = cmake_info.split('\n')[0] if cmake_info else "已安装"
        make_version = make_info.split('\n')[0] if make_info else "已安装"
        print_success(f"CMake和Make已安装，跳过")
        print_info(f"  CMake: {cmake_version}")
        print_info(f"  Make: {make_version}")
    else:
        if not install_cmake():
            print_error("CMake和Make安装失败")
            # 继续执行，不中断
    
    # 4. 安装OpenOCD
    print_header("步骤 4/7: 安装OpenOCD")
    openocd_installed, openocd_info = tool_status['openocd']
    
    if openocd_installed and not args.force:
        openocd_version = openocd_info.split('\n')[0] if openocd_info else "已安装"
        print_success("OpenOCD已安装，跳过")
        print_info(f"  OpenOCD: {openocd_version}")
    else:
        if not install_openocd():
            print_error("OpenOCD安装失败")
            # 继续执行，不中断
    
    # 5. 安装ARM GCC
    print_header("步骤 5/7: 安装ARM GCC")
    arm_gcc_installed, arm_gcc_info = tool_status['arm_gcc']
    
    if arm_gcc_installed and not args.force:
        arm_gcc_version = arm_gcc_info.split('\n')[0] if arm_gcc_info else "已安装"
        print_success("ARM GCC已安装，跳过")
        print_info(f"  ARM GCC: {arm_gcc_version}")
    else:
        # 通过pacman安装ARM GCC
        if not install_arm_gcc():
            print_warning("ARM GCC安装失败")
            print_info("请检查pacman仓库中是否有可用的ARM GCC工具链包")
    
    # 6. 配置环境变量
    print_header("步骤 6/7: 配置环境变量")
    if args.skip_env:
        print_warning("跳过环境变量配置（--skip-env）")
    else:
        if not configure_environment_variables(skip_if_not_admin=True):
            print_warning("环境变量配置失败，可能需要手动配置")
    
    # 验证安装
    print_header("验证安装")
    results = verify_all_tools()
    print_verification_summary(results)
    
    # 完成
    print_header("安装完成")
    print_success("工具链安装流程已完成！")
    print_info("\n下一步:")
    print_info("1. 如果配置了环境变量，请重新打开命令行窗口")
    print_info("2. 运行以下命令验证工具:")
    print_info("   cmake --version")
    print_info("   make --version")
    print_info("   openocd --version")
    print_info("   arm-none-eabi-gcc --version")

