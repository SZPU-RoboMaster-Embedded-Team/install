# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, WingetUtils, ChooseTask
from .base import osversion, osarch


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 MSYS2"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'

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

        # 检查默认安装路径
        import os
        default_paths = [
            r'C:\msys64',
            r'C:\msys32',
            os.path.expanduser(r'~\msys64'),
            os.path.expanduser(r'~\msys32')
        ]

        for path in default_paths:
            if os.path.exists(path):
                PrintUtils.print_success(f"检测到 MSYS2 已安装在: {path}")
                return True

        return False

    def install_msys2_with_winget(self):
        """使用 winget 安装 MSYS2"""
        PrintUtils.print_info("开始使用 winget 安装 MSYS2...")

        # MSYS2 的 winget 包 ID
        package_id = "MSYS2.MSYS2"

        # 使用默认安装路径 D:\wingetApp
        if WingetUtils.install(package_id, use_default_location=True):
            PrintUtils.print_success("MSYS2 安装成功!")
            PrintUtils.print_info(f"MSYS2 安装路径: {WingetUtils.DEFAULT_INSTALL_PATH}")
            PrintUtils.print_warning("注意: 如果 winget 不支持自定义路径，可能仍会安装到默认位置 C:\\msys64")
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

        import os
        msys2_path = r'C:\msys64'
        if not os.path.exists(msys2_path):
            msys2_path = os.path.expanduser(r'~\msys64')

        if not os.path.exists(msys2_path):
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

        import os
        msys2_path = r'C:\msys64'
        if not os.path.exists(msys2_path):
            msys2_path = os.path.expanduser(r'~\msys64')

        if not os.path.exists(msys2_path):
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
        """更新 MSYS2"""
        PrintUtils.print_info("正在更新 MSYS2...")
        PrintUtils.print_warning("更新过程中可能需要关闭并重新打开 MSYS2 终端")

        import os
        msys2_path = r'C:\msys64'
        if not os.path.exists(msys2_path):
            msys2_path = os.path.expanduser(r'~\msys64')

        if not os.path.exists(msys2_path):
            PrintUtils.print_error("未找到 MSYS2 安装目录")
            return False

        bash_path = os.path.join(msys2_path, 'usr', 'bin', 'bash.exe')

        if not os.path.exists(bash_path):
            PrintUtils.print_error("未找到 bash.exe")
            return False

        # 执行更新命令
        update_cmd = f'"{bash_path}" -lc "pacman -Syu --noconfirm"'
        result = CmdTask(update_cmd, os_command=True).run()

        if result:
            PrintUtils.print_success("MSYS2 更新完成")
            return True
        else:
            PrintUtils.print_warning("MSYS2 更新可能未完全成功，建议手动检查")
            return False

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
