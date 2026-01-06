# -*- coding: utf-8 -*-
"""
MSYS2安装和初始化模块
包括解压、初始化和pacman数据库更新
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Tuple, Optional

from install_toolchain import MSYS2_DIR, MSYS2_BASH, print_info, print_success, print_error, print_warning
from downloader import extract_archive


def install_msys2_from_exe(installer_path: Path, dest_dir: Path) -> bool:
    """
    从exe安装包安装MSYS2
    注意：MSYS2的exe安装程序是自解压文件，会解压到当前目录的msys64文件夹
    返回: 是否成功
    """
    try:
        print_info("开始安装MSYS2...")
        print_info("MSYS2安装程序是自解压文件，将自动解压...")
        
        # MSYS2安装程序会解压到当前目录的msys64文件夹
        # 我们需要在安装程序所在目录运行
        installer_dir = installer_path.parent
        msys64_dir = installer_dir / "msys64"
        
        # 检查是否已经解压过了
        if msys64_dir.exists() and (msys64_dir / "usr" / "bin" / "bash.exe").exists():
            print_info(f"发现已存在的MSYS2目录: {msys64_dir}")
        else:
            # 如果目标目录已存在，先删除
            if dest_dir.exists():
                print_warning(f"目标目录已存在，将删除: {dest_dir}")
                import shutil
                shutil.rmtree(dest_dir)
            
            # 如果msys64已存在但不完整，先删除
            if msys64_dir.exists():
                print_warning(f"发现已存在的msys64目录，将删除: {msys64_dir}")
                import shutil
                shutil.rmtree(msys64_dir)
            
            # 运行安装程序（自解压）
            print_info(f"正在启动安装程序: {installer_path}")
            print_info("请等待解压完成（这可能需要几分钟）...")
            
            # 在安装程序所在目录运行
            result = subprocess.run(
                [str(installer_path)],
                cwd=str(installer_dir),
                timeout=600  # 10分钟超时
            )
            
            # 等待一下，确保解压完成
            import time
            max_wait = 60  # 最多等待60秒
            waited = 0
            while waited < max_wait:
                if msys64_dir.exists() and (msys64_dir / "usr" / "bin" / "bash.exe").exists():
                    break
                time.sleep(1)
                waited += 1
                if waited % 5 == 0:
                    print_info(f"等待解压完成... ({waited}/{max_wait}秒)")
            
            # 检查msys64目录是否存在
            if not msys64_dir.exists():
                print_error(f"MSYS2解压失败，未找到msys64目录")
                return False
            
            # 检查bash是否存在
            bash_path = msys64_dir / "usr" / "bin" / "bash.exe"
            if not bash_path.exists():
                print_error(f"MSYS2解压不完整，未找到bash.exe")
                return False
        
        # 将msys64重命名为目标目录
        if msys64_dir.exists() and not dest_dir.exists():
            print_info(f"将msys64目录移动到目标位置: {dest_dir}")
            import shutil
            shutil.move(str(msys64_dir), str(dest_dir))
        elif msys64_dir.exists() and dest_dir.exists():
            # 如果目标目录已存在，先删除再移动
            print_warning(f"目标目录已存在，将删除后移动: {dest_dir}")
            import shutil
            shutil.rmtree(dest_dir)
            shutil.move(str(msys64_dir), str(dest_dir))
        
        # 再次检查
        if MSYS2_BASH.exists():
            print_success("MSYS2安装完成")
            return True
        else:
            print_error(f"MSYS2未在预期位置找到: {MSYS2_BASH}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("MSYS2解压超时")
        return False
    except Exception as e:
        print_error(f"MSYS2安装过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def install_msys2_from_archive(archive_path: Path, dest_dir: Path) -> bool:
    """
    从归档文件安装MSYS2（便携版）
    返回: 是否成功
    """
    try:
        print_info("从归档文件安装MSYS2...")
        
        # 解压到目标目录
        if extract_archive(archive_path, dest_dir):
            # 检查bash是否存在
            if MSYS2_BASH.exists():
                print_success("MSYS2解压完成")
                return True
            else:
                print_error("MSYS2解压后未找到bash.exe")
                return False
        else:
            return False
            
    except Exception as e:
        print_error(f"从归档文件安装MSYS2失败: {e}")
        return False


def initialize_msys2() -> bool:
    """
    初始化MSYS2环境
    更新pacman数据库
    返回: 是否成功
    """
    if not MSYS2_BASH.exists():
        print_error("MSYS2未安装，无法初始化")
        return False
    
    try:
        print_info("初始化MSYS2环境...")
        
        # 更新pacman数据库
        print_info("更新pacman数据库...")
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', 'pacman -Sy --noconfirm'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print_success("pacman数据库更新完成")
        else:
            print_warning(f"pacman数据库更新可能有问题: {result.stderr}")
            # 继续执行，可能只是警告
        
        # 更新pacman本身
        print_info("更新pacman...")
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', 'pacman -S --noconfirm pacman pacman-mirrors msys2-runtime'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print_success("pacman更新完成")
        else:
            print_warning(f"pacman更新可能有问题: {result.stderr}")
        
        # 再次更新数据库
        print_info("再次更新pacman数据库...")
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', 'pacman -Sy --noconfirm'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        print_success("MSYS2初始化完成")
        return True
        
    except subprocess.TimeoutExpired:
        print_error("MSYS2初始化超时")
        return False
    except Exception as e:
        print_error(f"MSYS2初始化失败: {e}")
        return False


def run_msys2_command(command: str, timeout: int = 60) -> Tuple[bool, str, str]:
    """
    在MSYS2环境中运行命令
    返回: (是否成功, stdout, stderr)
    """
    if not MSYS2_BASH.exists():
        return False, "", "MSYS2未安装"
    
    try:
        result = subprocess.run(
            [str(MSYS2_BASH), '-lc', command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 遇到编码错误时替换为占位符
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)


def check_msys2_ready() -> bool:
    """
    检查MSYS2是否已准备好使用
    返回: 是否就绪
    """
    if not MSYS2_BASH.exists():
        return False
    
    # 测试运行一个简单命令
    success, _, _ = run_msys2_command('echo "MSYS2 is ready"')
    return success

