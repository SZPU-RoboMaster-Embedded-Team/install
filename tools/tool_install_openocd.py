# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, WingetUtils, ChooseTask, EnvUtils, check_admin
from .base import osversion, osarch
import os
import sys
import platform
import subprocess

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 OpenOCD"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'

    def is_valid_msys2_path(self, path):
        """检查路径是否是有效的 MSYS2 安装目录
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 如果是有效的 MSYS2 安装目录返回 True，否则返回 False
        """
        if not path or not os.path.exists(path):
            return False
        
        # 检查关键文件/目录是否存在，以确认这是真正的 MSYS2 安装目录
        # 检查 usr\bin\bash.exe（MSYS2 的核心文件）
        bash_path = os.path.join(path, 'usr', 'bin', 'bash.exe')
        if os.path.exists(bash_path):
            return True
        
        # 检查 etc\pacman.d（pacman 配置目录）
        pacman_dir = os.path.join(path, 'etc', 'pacman.d')
        if os.path.exists(pacman_dir):
            return True
        
        # 如果路径本身是 msys64 或 msys32，也检查是否有 usr 目录
        path_name = os.path.basename(path.rstrip(os.sep))
        if path_name in ['msys64', 'msys32']:
            usr_dir = os.path.join(path, 'usr')
            if os.path.exists(usr_dir):
                return True
        
        return False

    def get_msys2_path(self):
        """获取 MSYS2 安装路径"""
        # 尝试从配置文件获取路径列表
        paths = None
        try:
            # 先尝试直接导入（base.py 可能已经添加了路径）
            import config
            if hasattr(config, 'MSYS2_PATHS'):
                paths = config.MSYS2_PATHS
        except ImportError:
            # 如果导入失败，尝试添加路径后再次导入
            try:
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                import config
                if hasattr(config, 'MSYS2_PATHS'):
                    paths = config.MSYS2_PATHS
            except:
                pass
        
        # 如果配置文件中没有，使用默认路径列表
        if paths is None:
            paths = [
                r'C:\msys64',
                r'C:\msys32',
                os.path.expanduser(r'~\msys64'),
                os.path.expanduser(r'~\msys32')
            ]
        
        # 遍历路径列表，返回第一个有效的 MSYS2 安装路径
        for path in paths:
            # 检查路径名，判断是否是可能包含MSYS2子目录的父目录
            path_name = os.path.basename(path.rstrip(os.sep))
            is_likely_parent_dir = path_name not in ['msys64', 'msys32']
            
            # 对于可能包含MSYS2子目录的父目录（如D:\CodeTools），
            # 优先检查子目录，避免误判：如果D:\CodeTools存在但D:\CodeTools\msys64不存在，
            # 说明MSYS2已经卸载，不应该返回D:\CodeTools
            if is_likely_parent_dir and os.path.exists(path):
                # 先检查常见的 MSYS2 子目录
                for subdir in ['msys64', 'msys32']:
                    sub_path = os.path.join(path, subdir)
                    if self.is_valid_msys2_path(sub_path):
                        return sub_path
                
                # 如果没有找到有效的子目录，继续检查下一个路径
                # 不检查父目录本身，因为如果子目录不存在，说明MSYS2已经卸载
                continue
            
            # 对于明确的MSYS2目录（如C:\msys64）或子目录检查失败的情况，
            # 检查路径本身是否是有效的 MSYS2 安装目录
            if self.is_valid_msys2_path(path):
                return path
        
        return None

    def check_msys2_installed(self):
        """检查 MSYS2 是否已安装"""
        msys2_path = self.get_msys2_path()
        if msys2_path:
            PrintUtils.print_success(f"检测到 MSYS2 已安装在: {msys2_path}")
            return True
        return False

    def install_package(self, bash_path, package_name, display_name):
        """安装单个包
        
        Args:
            bash_path: MSYS2 bash.exe 的路径
            package_name: 包名（pacman 中的名称）
            display_name: 显示名称（用于提示信息）
            
        Returns:
            bool: 安装是否成功
        """
        try:
            PrintUtils.print_info(f"正在安装 {display_name}...")
            
            result = subprocess.run(
                [bash_path, '-lc', f'pacman -S {package_name} --noconfirm'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                PrintUtils.print_success(f"{display_name} 安装完成!")
                return True
            else:
                PrintUtils.print_error(f"{display_name} 安装失败，返回码: {result.returncode}")
                if result.stderr:
                    # 只显示关键错误信息，避免输出过长
                    error_lines = result.stderr.split('\n')
                    for line in error_lines[-5:]:  # 只显示最后5行错误信息
                        if line.strip():
                            PrintUtils.print_warning(f"  {line.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            PrintUtils.print_error(f"{display_name} 安装超时（超过5分钟）")
            PrintUtils.print_warning("请检查网络连接或手动运行安装命令")
            return False
        except Exception as e:
            PrintUtils.print_error(f"{display_name} 安装过程中发生错误: {e}")
            return False

    def install_openocd(self):
        """使用 pacman 安装 OpenOCD"""
        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_error("未找到 MSYS2 安装目录")
            PrintUtils.print_warning("请先安装 MSYS2，然后再运行此工具")
            return False

        bash_path = os.path.join(msys2_path, 'usr', 'bin', 'bash.exe')
        if not os.path.exists(bash_path):
            PrintUtils.print_error(f"未找到 bash.exe，路径: {bash_path}")
            return False

        PrintUtils.print_info("开始安装 OpenOCD...")
        PrintUtils.print_info("")
        
        # 安装 OpenOCD 包
        package_name = 'mingw-w64-x86_64-openocd'
        display_name = 'OpenOCD'
        
        if self.install_package(bash_path, package_name, display_name):
            PrintUtils.print_success("OpenOCD 安装完成!")
            return True
        else:
            PrintUtils.print_error("OpenOCD 安装失败")
            return False

    def run(self):
        """运行安装流程"""
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("OpenOCD 一键安装工具")
        PrintUtils.print_info("通过 MSYS2 的 pacman 包管理器安装 OpenOCD")
        PrintUtils.print_info("=" * 60)

        # 检查 MSYS2 是否已安装
        if not self.check_msys2_installed():
            PrintUtils.print_error("未检测到 MSYS2 安装")
            PrintUtils.print_info("请先使用工具 1 安装 MSYS2，然后再运行此工具")
            PrintUtils.print_info("MSYS2 是安装 OpenOCD 的前置依赖")
            return

        # 执行安装
        if self.install_openocd():
            PrintUtils.print_success("=" * 60)
            PrintUtils.print_success("安装完成!")
            PrintUtils.print_info("")
            PrintUtils.print_info("使用说明:")
            PrintUtils.print_info("  1. 在 MSYS2 终端中使用 openocd")
            PrintUtils.print_info("  2. 或者将 MSYS2 的 bin 目录添加到系统 PATH 环境变量")
            PrintUtils.print_info("")
            PrintUtils.print_info("验证安装:")
            PrintUtils.print_info("  在 MSYS2 终端中运行以下命令:")
            PrintUtils.print_info("    openocd --version")
            PrintUtils.print_success("=" * 60)
        else:
            PrintUtils.print_error("=" * 60)
            PrintUtils.print_error("安装失败")
            PrintUtils.print_info("如果遇到问题，请检查:")
            PrintUtils.print_info("  1. MSYS2 是否正确安装")
            PrintUtils.print_info("  2. 网络连接是否正常")
            PrintUtils.print_info("  3. 是否有足够的磁盘空间")
            PrintUtils.print_error("=" * 60)

