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
        self.name = "一键安装 MSYS2"
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
        import subprocess
        try:
            result = subprocess.run(
                ['where', 'msys2'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                PrintUtils.print_success("检测到 MSYS2 已安装")
                return True
        except:
            pass

        # 使用统一的方法检查安装路径
        msys2_path = self.get_msys2_path()
        if msys2_path:
            PrintUtils.print_success(f"检测到 MSYS2 已安装在: {msys2_path}")
            return True

        return False

    def install_msys2_with_winget(self):
        """使用 winget 安装 MSYS2"""
        PrintUtils.print_info("开始使用 winget 安装 MSYS2...")

        # MSYS2 的 winget 包 ID
        package_id = "MSYS2.MSYS2"

        # 显示 winget 下载文件的存储位置
        winget_download_path = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            'Microsoft', 'WinGet', 'Packages'
        )
        temp_path = os.environ.get('TEMP', '')
        PrintUtils.print_info(f"下载文件存储位置:")
        PrintUtils.print_info(f"  - Winget 缓存目录: {winget_download_path}")
        PrintUtils.print_info(f"  - 系统临时目录: {temp_path}")
        PrintUtils.print_info(f"  (安装程序下载后会自动运行，通常不会保留在临时目录)")

        # 获取 MSYS2 的期望安装路径（从配置文件读取第一个路径）
        msys2_install_path = None
        try:
            import config
            if hasattr(config, 'MSYS2_PATHS') and len(config.MSYS2_PATHS) > 0:
                msys2_install_path = config.MSYS2_PATHS[0]
        except:
            # 如果无法读取配置，使用默认路径
            msys2_install_path = r'C:\msys64'

        # 使用指定的 MSYS2 安装路径
        if msys2_install_path:
            PrintUtils.print_info(f"尝试将 MSYS2 安装到: {msys2_install_path}")
            success = WingetUtils.install(package_id, custom_location=msys2_install_path)
        else:
            # 如果无法获取路径，使用默认行为
            success = WingetUtils.install(package_id, use_default_location=True)

        if success:
            PrintUtils.print_success("MSYS2 安装成功!")
            if msys2_install_path:
                PrintUtils.print_info(f"MSYS2 安装路径: {msys2_install_path}")

            return True
        else:
            PrintUtils.print_error("MSYS2 安装失败")
            return False

    def uninstall_msys2_with_winget(self):
        """使用 winget 卸载 MSYS2"""
        PrintUtils.print_info("开始使用 winget 卸载 MSYS2...")

        # MSYS2 的 winget 包 ID
        package_id = "MSYS2.MSYS2"

        # 先检查已安装的版本
        PrintUtils.print_info("正在检查已安装的 MSYS2 版本...")
        versions = WingetUtils.list_installed_versions(package_id)
        
        if not versions:
            PrintUtils.print_warning("未找到已安装的 MSYS2 版本")
            # 尝试直接卸载（可能 winget list 格式不同）
            PrintUtils.print_info("尝试直接卸载...")
            versions = ["未知版本"]

        if len(versions) > 1:
            PrintUtils.print_warning(f"检测到已安装多个版本的 MSYS2: {', '.join(versions)}")
            PrintUtils.print_info("选项:")
            PrintUtils.print_info("  1. 卸载所有版本")
            PrintUtils.print_info("  2. 取消卸载")
            
            choice = input("请选择 [1/2]: ").strip()
            if choice != '1':
                PrintUtils.print_info("取消卸载")
                return False
            
            # 确认卸载所有版本
            PrintUtils.print_warning("警告: 此操作将卸载所有已安装的 MSYS2 版本")
            confirm = input("确定要继续卸载所有版本吗？[y/N]: ").strip().lower()
            if confirm not in ['y', 'yes']:
                PrintUtils.print_info("取消卸载")
                return False
            
            # 使用 --all-versions 卸载所有版本
            if WingetUtils.uninstall(package_id, all_versions=True):
                PrintUtils.print_success("MSYS2 所有版本卸载成功!")
                PrintUtils.print_warning("注意: 可能需要手动删除安装目录（如 C:\\msys64）")
                return True
            else:
                PrintUtils.print_error("MSYS2 卸载失败")
                return False
        else:
            # 只有一个版本或未检测到版本，直接卸载
            if len(versions) == 1:
                PrintUtils.print_info(f"检测到已安装版本: {versions[0]}")
            
            # 确认卸载
            PrintUtils.print_warning("警告: 此操作将卸载 MSYS2")
            confirm = input("确定要继续卸载吗？[y/N]: ").strip().lower()
            if confirm not in ['y', 'yes']:
                PrintUtils.print_info("取消卸载")
                return False

            if WingetUtils.uninstall(package_id):
                PrintUtils.print_success("MSYS2 卸载成功!")
                PrintUtils.print_warning("注意: 可能需要手动删除安装目录（如 C:\\msys64）")
                return True
            else:
                PrintUtils.print_error("MSYS2 卸载失败")
                PrintUtils.print_warning("提示: 如果检测到多个版本，请使用选项 1 卸载所有版本")
                return False

    def install_msys2_manual(self):
        """手动下载安装 MSYS2"""
        PrintUtils.print_info("开始手动下载安装 MSYS2...")

        # 根据架构选择下载链接
        if osarch == 'amd64':
            download_url = "https://repo.msys2.org/distrib/x86_64/msys2-x86_64-latest.exe"
            installer_name = "msys2-x86_64-latest.exe"
        else:
            PrintUtils.print_error(f"不支持的架构: {osarch}")
            return False

        import os
        temp_dir = os.environ.get('TEMP', '.')
        installer_path = os.path.join(temp_dir, installer_name)

        # 下载安装程序
        if not FileUtils.download(download_url, installer_path):
            return False

        # 运行安装程序
        PrintUtils.print_info("正在运行安装程序，请按照提示完成安装...")
        PrintUtils.print_warning("注意: 建议使用默认安装路径 C:\\msys64")

        result = CmdTask(f'"{installer_path}"', os_command=True).run()

        # 清理安装程序
        try:
            os.remove(installer_path)
            PrintUtils.print_info("已清理安装程序")
        except:
            pass

        if result:
            PrintUtils.print_success("MSYS2 安装完成!")
            return True
        else:
            PrintUtils.print_error("MSYS2 安装失败")
            return False

    def configure_msys2(self):
        """配置 MSYS2"""
        PrintUtils.print_info("开始配置 MSYS2...")

        # 询问是否配置镜像源
        options = {
            1: "配置国内镜像源（清华源，推荐）",
            2: "配置国内镜像源（中科大源）",
            3: "跳过镜像源配置"
        }

        code, result = ChooseTask(options, "是否配置 MSYS2 镜像源？").run()

        if code == 0:
            return

        if code == 1:
            self.configure_tsinghua_mirror()
        elif code == 2:
            self.configure_ustc_mirror()
        else:
            PrintUtils.print_info("跳过镜像源配置")

        # 更新系统
        PrintUtils.print_info("建议首次安装后更新 MSYS2 系统")
        update_choice = input("是否现在更新 MSYS2？[y/N]: ").strip().lower()

        if update_choice in ['y', 'yes']:
            self.update_msys2()

    def configure_tsinghua_mirror(self):
        """配置清华镜像源"""
        PrintUtils.print_info("配置清华大学镜像源...")

        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_error("未找到 MSYS2 安装目录")
            return False

        mirrorlist_path = os.path.join(msys2_path, 'etc', 'pacman.d', 'mirrorlist.mingw64')

        mirror_content = """##
## MSYS2 repository mirrorlist
##

## Tsinghua University (China)
Server = https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/x86_64
"""

        try:
            # 备份原文件
            if os.path.exists(mirrorlist_path):
                import shutil
                shutil.copy(mirrorlist_path, mirrorlist_path + '.bak')

            with open(mirrorlist_path, 'w', encoding='utf-8') as f:
                f.write(mirror_content)

            PrintUtils.print_success("清华镜像源配置成功")
            return True
        except Exception as e:
            PrintUtils.print_error(f"配置镜像源失败: {str(e)}")
            return False

    def configure_ustc_mirror(self):
        """配置中科大镜像源"""
        PrintUtils.print_info("配置中国科学技术大学镜像源...")

        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_error("未找到 MSYS2 安装目录")
            return False

        mirrorlist_path = os.path.join(msys2_path, 'etc', 'pacman.d', 'mirrorlist.mingw64')

        mirror_content = """##
## MSYS2 repository mirrorlist
##

## USTC (China)
Server = https://mirrors.ustc.edu.cn/msys2/mingw/x86_64
"""

        try:
            # 备份原文件
            if os.path.exists(mirrorlist_path):
                import shutil
                shutil.copy(mirrorlist_path, mirrorlist_path + '.bak')

            with open(mirrorlist_path, 'w', encoding='utf-8') as f:
                f.write(mirror_content)

            PrintUtils.print_success("中科大镜像源配置成功")
            return True
        except Exception as e:
            PrintUtils.print_error(f"配置镜像源失败: {str(e)}")
            return False

    def update_msys2(self):
        """初始化 MSYS2 环境，更新 pacman 数据库"""
        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_error("未找到 MSYS2 安装目录")
            return False

        bash_path = os.path.join(msys2_path, 'usr', 'bin', 'bash.exe')
        if not os.path.exists(bash_path):
            PrintUtils.print_error(f"未找到 bash.exe，路径: {bash_path}")
            return False

        try:
            PrintUtils.print_info("初始化 MSYS2 环境...")
            
            # 更新 pacman 数据库
            PrintUtils.print_info("更新 pacman 数据库...")
            result = subprocess.run(
                [bash_path, '-lc', 'pacman -Sy --noconfirm'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )
            
            if result.returncode == 0:
                PrintUtils.print_success("pacman 数据库更新完成")
            else:
                PrintUtils.print_warning(f"pacman 数据库更新可能有问题: {result.stderr}")
                # 继续执行，可能只是警告
            
            # 更新 pacman 本身
            PrintUtils.print_info("更新 pacman...")
            result = subprocess.run(
                [bash_path, '-lc', 'pacman -S --noconfirm pacman pacman-mirrors msys2-runtime'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )
            
            if result.returncode == 0:
                PrintUtils.print_success("pacman 更新完成")
            else:
                PrintUtils.print_warning(f"pacman 更新可能有问题: {result.stderr}")
            
            # 再次更新数据库
            PrintUtils.print_info("再次更新 pacman 数据库...")
            result = subprocess.run(
                [bash_path, '-lc', 'pacman -Sy --noconfirm'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300
            )
            
            PrintUtils.print_success("MSYS2 初始化完成")
            return True
            
        except subprocess.TimeoutExpired:
            PrintUtils.print_error("MSYS2 初始化超时")
            return False
        except Exception as e:
            PrintUtils.print_error(f"MSYS2 初始化失败: {e}")
            return False

    def get_msys2_paths(self, msys2_base_path):
        """获取需要添加到PATH的MSYS2路径
        
        Args:
            msys2_base_path: MSYS2的安装路径（字符串）
            
        Returns:
            list: 路径列表（字符串）
        """
        paths = []
        
        if not msys2_base_path or not os.path.exists(msys2_base_path):
            return paths
        
        # MSYS2的主要bin目录
        msys2_bin = os.path.join(msys2_base_path, 'usr', 'bin')
        if os.path.exists(msys2_bin):
            paths.append(msys2_bin)
        
        # MinGW64的bin目录
        mingw64_bin = os.path.join(msys2_base_path, 'mingw64', 'bin')
        if os.path.exists(mingw64_bin):
            paths.append(mingw64_bin)
        
        # UCRT64的bin目录
        ucrt64_bin = os.path.join(msys2_base_path, 'ucrt64', 'bin')
        if os.path.exists(ucrt64_bin):
            paths.append(ucrt64_bin)
        
        return paths

    def configure_environment_variables(self):
        """配置 MSYS2 环境变量"""
        msys2_path = self.get_msys2_path()
        if not msys2_path:
            PrintUtils.print_warning("未找到 MSYS2 安装目录，跳过环境变量配置")
            return False

        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("MSYS2 环境变量配置")
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("是否将 MSYS2 的 bin 目录添加到系统 PATH 环境变量？")
        PrintUtils.print_info("这将允许你在任何命令行窗口直接使用 MSYS2 工具")
        
        choice = input("是否配置环境变量？[y/N]: ").strip().lower()
        if choice not in ['y', 'yes']:
            PrintUtils.print_info("跳过环境变量配置")
            return False

        # 获取需要添加的路径
        paths = self.get_msys2_paths(msys2_path)
        if not paths:
            PrintUtils.print_warning("没有找到需要添加到PATH的路径")
            return False

        # 配置环境变量（使用通用方法）
        success = EnvUtils.configure_path_environment(paths, skip_if_not_admin=True)
        return success

    def run(self):
        """运行安装流程"""
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("MSYS2 一键安装工具")
        PrintUtils.print_info("MSYS2 是一个在 Windows 上提供类 Unix 环境的工具集")
        PrintUtils.print_info("=" * 60)

        # 检查是否已安装
        if self.check_msys2_installed():
            # 选择操作
            options = {
                1: "重新安装 MSYS2",
                2: "配置 MSYS2",
                3: "卸载 MSYS2（使用 winget）",
                4: "退出"
            }
            
            code, result = ChooseTask(options, "MSYS2 已安装，请选择操作:").run()
            
            if code == 0 or code == 4:
                PrintUtils.print_info("退出")
                return
            elif code == 1:
                # 重新安装流程
                pass  # 继续执行下面的安装流程
            elif code == 2:
                # 配置 MSYS2
                self.configure_msys2()
                return
            elif code == 3:
                # 卸载 MSYS2
                self.uninstall_msys2_with_winget()
                return
        else:
            # 未安装，直接进入安装流程
            pass

        # 选择安装方式
        options = {
            1: "使用 winget 安装（推荐，自动化程度高）",
            2: "手动下载安装（适合 winget 不可用的情况）"
        }

        code, result = ChooseTask(options, "请选择安装方式:").run()

        if code == 0:
            PrintUtils.print_info("取消安装")
            return

        success = False
        if code == 1:
            success = self.install_msys2_with_winget()
        elif code == 2:
            success = self.install_msys2_manual()

        if success:
            # 安装成功后进行配置
            self.configure_msys2()
            
            # 配置环境变量
            self.configure_environment_variables()

            PrintUtils.print_success("=" * 60)
            PrintUtils.print_success("MSYS2 安装完成!")
            PrintUtils.print_info("你可以通过以下方式启动 MSYS2:")
            PrintUtils.print_info("  1. 在开始菜单搜索 'MSYS2'")
            PrintUtils.print_info("  2. 运行 C:\\msys64\\msys2.exe")
            PrintUtils.print_info("")
            PrintUtils.print_info("常用的 MSYS2 环境:")
            PrintUtils.print_info("  - MSYS2 MSYS: 通用 Unix 环境")
            PrintUtils.print_info("  - MSYS2 MINGW64: 64位 MinGW 开发环境")
            PrintUtils.print_info("  - MSYS2 MINGW32: 32位 MinGW 开发环境")
            PrintUtils.print_success("=" * 60)
