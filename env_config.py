# -*- coding: utf-8 -*-
"""
环境变量配置模块
自动添加PATH到系统环境变量
"""

import os
import sys
from pathlib import Path
from typing import List

from install_toolchain import MSYS2_DIR, print_info, print_success, print_error, print_warning, check_admin


def get_msys2_paths() -> List[Path]:
    """
    获取需要添加到PATH的MSYS2路径
    返回: 路径列表
    """
    paths = []
    
    # MSYS2的主要bin目录
    msys2_bin = MSYS2_DIR / "usr" / "bin"
    if msys2_bin.exists():
        paths.append(msys2_bin)
    
    # MinGW64的bin目录
    mingw64_bin = MSYS2_DIR / "mingw64" / "bin"
    if mingw64_bin.exists():
        paths.append(mingw64_bin)
    
    # UCRT64的bin目录
    ucrt64_bin = MSYS2_DIR / "ucrt64" / "bin"
    if ucrt64_bin.exists():
        paths.append(ucrt64_bin)
    
    # ARM GCC的bin目录（如果已安装）
    arm_gcc_bin = MSYS2_DIR / "opt" / "arm-gcc" / "bin"
    if arm_gcc_bin.exists():
        paths.append(arm_gcc_bin)
    
    return paths


def add_to_system_path(paths: List[Path], skip_if_not_admin: bool = True) -> bool:
    """
    添加路径到系统PATH环境变量
    返回: 是否成功
    """
    if not check_admin():
        if skip_if_not_admin:
            print_warning("需要管理员权限来修改系统环境变量")
            print_info("请以管理员身份运行此脚本，或使用 --skip-env 跳过环境变量配置")
            return False
        else:
            print_error("需要管理员权限")
            return False
    
    try:
        import winreg
        
        # 打开系统环境变量注册表项
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # 获取当前的PATH值
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path = ""
        
        # 转换为列表
        path_list = [p.strip() for p in current_path.split(os.pathsep) if p.strip()]
        
        # 添加新路径（如果不存在）
        added_paths = []
        for path in paths:
            path_str = str(path.absolute())
            if path_str not in path_list:
                path_list.append(path_str)
                added_paths.append(path_str)
        
        if added_paths:
            # 更新PATH
            new_path = os.pathsep.join(path_list)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # 广播环境变量更改消息
            import ctypes
            ctypes.windll.user32.SendMessageW(
                0xFFFF,  # HWND_BROADCAST
                0x001A,  # WM_SETTINGCHANGE
                0,
                "Environment"
            )
            
            print_success(f"已添加以下路径到系统PATH:")
            for p in added_paths:
                print_info(f"  - {p}")
            print_warning("请重新打开命令行窗口以使环境变量生效")
            return True
        else:
            winreg.CloseKey(key)
            print_info("所有路径已存在于系统PATH中")
            return True
            
    except Exception as e:
        print_error(f"修改系统环境变量失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_to_user_path(paths: List[Path]) -> bool:
    """
    添加路径到用户PATH环境变量（不需要管理员权限）
    返回: 是否成功
    """
    try:
        import winreg
        
        # 打开用户环境变量注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # 获取当前的PATH值
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path = ""
        
        # 转换为列表
        path_list = [p.strip() for p in current_path.split(os.pathsep) if p.strip()]
        
        # 添加新路径（如果不存在）
        added_paths = []
        for path in paths:
            path_str = str(path.absolute())
            if path_str not in path_list:
                path_list.append(path_str)
                added_paths.append(path_str)
        
        if added_paths:
            # 更新PATH
            new_path = os.pathsep.join(path_list)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # 广播环境变量更改消息
            import ctypes
            ctypes.windll.user32.SendMessageW(
                0xFFFF,  # HWND_BROADCAST
                0x001A,  # WM_SETTINGCHANGE
                0,
                "Environment"
            )
            
            print_success(f"已添加以下路径到用户PATH:")
            for p in added_paths:
                print_info(f"  - {p}")
            print_warning("请重新打开命令行窗口以使环境变量生效")
            return True
        else:
            winreg.CloseKey(key)
            print_info("所有路径已存在于用户PATH中")
            return True
            
    except Exception as e:
        print_error(f"修改用户环境变量失败: {e}")
        return False


def configure_environment_variables(skip_if_not_admin: bool = True) -> bool:
    """
    配置环境变量
    返回: 是否成功
    """
    paths = get_msys2_paths()
    
    if not paths:
        print_warning("没有找到需要添加到PATH的路径")
        return False
    
    # 尝试添加到系统PATH（需要管理员权限）
    if check_admin():
        return add_to_system_path(paths, skip_if_not_admin=False)
    else:
        # 如果没有管理员权限，添加到用户PATH
        if skip_if_not_admin:
            print_warning("没有管理员权限，将添加到用户PATH")
            return add_to_user_path(paths)
        else:
            print_error("需要管理员权限")
            return False

