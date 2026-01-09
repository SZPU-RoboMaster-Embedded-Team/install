# -*- coding: utf-8 -*-
"""
下载模块
支持从官方源下载MSYS2安装包和ARM GCC
"""

import os
import sys
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from install_toolchain import print_info, print_success, print_error, print_warning, Colors

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print_warning("未安装tqdm，将不显示下载进度条")


def download_file(url: str, dest_path: Path, show_progress: bool = True) -> bool:
    """
    下载文件
    返回: 是否成功
    """
    try:
        print_info(f"开始下载: {url}")
        print_info(f"保存到: {dest_path}")
        
        # 创建目标目录
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 下载文件
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        if show_progress and HAS_TQDM and total_size > 0:
            with open(dest_path, 'wb') as f, tqdm(
                desc=dest_path.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        else:
            downloaded = 0
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and not HAS_TQDM:
                            percent = (downloaded / total_size) * 100
                            print(f"\r下载进度: {percent:.1f}%", end='', flush=True)
            
            if not HAS_TQDM:
                print()  # 换行
        
        print_success(f"下载完成: {dest_path.name}")
        return True
        
    except requests.exceptions.RequestException as e:
        print_error(f"下载失败: {e}")
        if dest_path.exists():
            dest_path.unlink()  # 删除不完整的文件
        return False
    except Exception as e:
        print_error(f"下载过程中发生错误: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def get_latest_msys2_url() -> Optional[str]:
    """
    获取最新MSYS2安装包的下载URL
    返回: 下载URL或None
    """
    # MSYS2的GitHub releases API
    api_url = "https://api.github.com/repos/msys2/msys2-installer/releases/latest"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 查找Windows安装包
        for asset in data.get('assets', []):
            name = asset['name']
            if 'x86_64' in name and name.endswith('.exe'):
                return asset['browser_download_url']
        
        # 如果没有找到exe，尝试zip格式
        for asset in data.get('assets', []):
            name = asset['name']
            if 'x86_64' in name and (name.endswith('.zip') or name.endswith('.tar.xz')):
                return asset['browser_download_url']
        
    except Exception as e:
        print_warning(f"无法从GitHub获取MSYS2最新版本: {e}")
    
    # 备用URL（可能需要手动更新版本号）
    return "https://github.com/msys2/msys2-installer/releases/latest/download/msys2-x86_64-latest.exe"


def get_latest_arm_gcc_url() -> Optional[str]:
    """
    获取最新ARM GCC工具链的下载URL
    返回: 下载URL或None
    注意：ARM官方没有公开API，此函数返回None，需要用户手动指定
    """
    # ARM官方下载页面需要手动访问
    # 访问: https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
    # 选择: Windows (mingw-w64-i686) -> arm-none-eabi -> 最新版本
    
    print_warning("ARM GCC需要手动下载")
    print_info("请访问: https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads")
    print_info("下载后使用 --arm-gcc-archive 参数指定文件路径")
    
    return None  # 返回None表示需要手动指定


def extract_archive(archive_path: Path, extract_to: Path, archive_type: Optional[str] = None) -> bool:
    """
    解压归档文件
    支持: .zip, .tar.xz, .tar.gz, .tar.bz2
    返回: 是否成功
    """
    try:
        print_info(f"解压: {archive_path.name} -> {extract_to}")
        
        extract_to.mkdir(parents=True, exist_ok=True)
        
        if archive_type is None:
            # 根据扩展名判断
            suffix = archive_path.suffix.lower()
            if suffix == '.zip':
                archive_type = 'zip'
            elif suffix == '.xz' or archive_path.name.endswith('.tar.xz'):
                archive_type = 'tar.xz'
            elif suffix == '.gz' or archive_path.name.endswith('.tar.gz'):
                archive_type = 'tar.gz'
            elif suffix == '.bz2' or archive_path.name.endswith('.tar.bz2'):
                archive_type = 'tar.bz2'
            else:
                print_error(f"不支持的归档格式: {suffix}")
                return False
        
        if archive_type == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_type in ['tar.xz', 'tar.gz', 'tar.bz2']:
            mode = 'r'
            if archive_type == 'tar.xz':
                mode = 'r:xz'
            elif archive_type == 'tar.gz':
                mode = 'r:gz'
            elif archive_type == 'tar.bz2':
                mode = 'r:bz2'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                # 解压时去除顶层目录（如果有）
                tar_ref.extractall(extract_to)
        else:
            print_error(f"不支持的归档类型: {archive_type}")
            return False
        
        print_success(f"解压完成: {extract_to}")
        return True
        
    except Exception as e:
        print_error(f"解压失败: {e}")
        return False


def download_msys2(dest_dir: Path, force: bool = False) -> Tuple[bool, Optional[Path]]:
    """
    下载MSYS2安装包
    返回: (是否成功, 安装包路径)
    """
    # 检查是否已存在
    installer_path = dest_dir / "msys2-installer.exe"
    if installer_path.exists() and not force:
        print_info(f"MSYS2安装包已存在: {installer_path}")
        return True, installer_path
    
    # 获取下载URL
    url = get_latest_msys2_url()
    if not url:
        print_error("无法获取MSYS2下载URL")
        return False, None
    
    # 下载
    if download_file(url, installer_path):
        return True, installer_path
    else:
        return False, None


def download_arm_gcc(dest_dir: Path, force: bool = False, custom_url: Optional[str] = None) -> Tuple[bool, Optional[Path]]:
    """
    下载ARM GCC工具链
    返回: (是否成功, 归档文件路径)
    """
    if custom_url:
        url = custom_url
    else:
        url = get_latest_arm_gcc_url()
        if not url:
            print_error("无法获取ARM GCC下载URL，请使用--arm-gcc-url参数指定")
            return False, None
    
    # 从URL提取文件名
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "arm-gnu-toolchain.tar.xz"
    
    archive_path = dest_dir / filename
    
    # 检查是否已存在
    if archive_path.exists() and not force:
        print_info(f"ARM GCC归档文件已存在: {archive_path}")
        return True, archive_path
    
    # 下载
    if download_file(url, archive_path):
        return True, archive_path
    else:
        return False, None

