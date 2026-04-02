# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, EnvUtils
import os
import sys
import subprocess


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 ARM GCC 工具链"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'
        self.package_name = 'mingw-w64-x86_64-arm-none-eabi-gcc'
        self.package_display_name = 'ARM GCC (arm-none-eabi-gcc)'

    def is_valid_msys2_path(self, path):
        if not path or not os.path.exists(path):
            return False
        bash_path = os.path.join(path, 'usr', 'bin', 'bash.exe')
        if os.path.exists(bash_path):
            return True
        pacman_dir = os.path.join(path, 'etc', 'pacman.d')
        return os.path.exists(pacman_dir)

    def get_msys2_path(self):
        paths = None
        try:
            import config
            if hasattr(config, 'MSYS2_PATHS'):
                paths = config.MSYS2_PATHS
        except ImportError:
            try:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                import config
                if hasattr(config, 'MSYS2_PATHS'):
                    paths = config.MSYS2_PATHS
            except Exception:
                pass

        if paths is None:
            paths = [r'C:\msys64', r'C:\msys32', os.path.expanduser(r'~\msys64')]

        for path in paths:
            path_name = os.path.basename(path.rstrip(os.sep))
            is_likely_parent = path_name not in ['msys64', 'msys32']
            if is_likely_parent and os.path.exists(path):
                for subdir in ['msys64', 'msys32']:
                    sub_path = os.path.join(path, subdir)
                    if self.is_valid_msys2_path(sub_path):
                        return sub_path
                continue
            if self.is_valid_msys2_path(path):
                return path
        return None

    def check_package_installed(self, bash_path, package_name):
        try:
            result = subprocess.run(
                [bash_path, '-lc', f'pacman -Q {package_name}'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_package(self, bash_path, package_name, display_name):
        try:
            PrintUtils.print_info(f"正在安装 {display_name}...")
            result = subprocess.run(
                [bash_path, '-lc', f'pacman -S {package_name} --noconfirm'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600
            )
            if result.returncode == 0:
                PrintUtils.print_success(f"{display_name} 安装完成!")
                return True

            PrintUtils.print_error(f"{display_name} 安装失败，返回码: {result.returncode}")
            if result.stderr:
                for line in result.stderr.split('\n')[-5:]:
                    if line.strip():
                        PrintUtils.print_warning(f"  {line.strip()}")
            return False
        except subprocess.TimeoutExpired:
            PrintUtils.print_error(f"{display_name} 安装超时（超过10分钟）")
            return False
        except Exception as e:
            PrintUtils.print_error(f"{display_name} 安装过程中发生错误: {e}")
            return False

    def add_arm_gcc_path(self, msys2_path):
        mingw_bin = os.path.join(msys2_path, 'mingw64', 'bin')
        gcc_exe = os.path.join(mingw_bin, 'arm-none-eabi-gcc.exe')
        if not os.path.exists(gcc_exe):
            PrintUtils.print_warning("未在 mingw64/bin 中检测到 arm-none-eabi-gcc.exe，跳过 PATH 配置")
            return False
        if EnvUtils.add_to_system_path([mingw_bin], skip_if_not_admin=True):
            PrintUtils.print_success(f"已添加到 PATH: {mingw_bin}")
            return True
        PrintUtils.print_warning("添加 PATH 失败，请手动添加")
        return False

    def run(self):
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("ARM GCC 工具链一键安装工具")
        PrintUtils.print_info("通过 MSYS2 的 pacman 包管理器安装 ARM GCC")
        PrintUtils.print_info("=" * 60)

        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_error("未检测到 MSYS2 安装")
            PrintUtils.print_info("请先使用工具 1 安装 MSYS2，然后再运行此工具")
            return

        PrintUtils.print_success(f"检测到 MSYS2 已安装在: {msys2_path}")
        bash_path = os.path.join(msys2_path, 'usr', 'bin', 'bash.exe')
        if not os.path.exists(bash_path):
            PrintUtils.print_error(f"未找到 bash.exe，路径: {bash_path}")
            return

        if self.check_package_installed(bash_path, self.package_name):
            PrintUtils.print_success(f"检测到 {self.package_display_name} 已安装")
            choice = input("是否重新安装？[y/N]: ").strip().lower()
            if choice not in ['y', 'yes']:
                add_path = input("是否将 MSYS2 mingw64\\bin 添加到 PATH？[Y/n]: ").strip().lower()
                if add_path not in ['n', 'no']:
                    self.add_arm_gcc_path(msys2_path)
                return

        if not self.install_package(bash_path, self.package_name, self.package_display_name):
            PrintUtils.print_error("=" * 60)
            PrintUtils.print_error("安装失败")
            PrintUtils.print_error("=" * 60)
            return

        self.add_arm_gcc_path(msys2_path)
        PrintUtils.print_success("=" * 60)
        PrintUtils.print_success("安装完成!")
        PrintUtils.print_info("验证命令: arm-none-eabi-gcc --version")
        PrintUtils.print_success("=" * 60)

