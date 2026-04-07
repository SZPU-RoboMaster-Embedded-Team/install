# -*- coding: utf-8 -*-
import os

from .base import BaseTool
from .base import PrintUtils, WingetUtils, ChooseTask


class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 Git for Windows"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "小鱼"

    def _get_git_install_path(self):
        """根据安装根目录计算 Git 目标路径。"""
        base_path = WingetUtils.DEFAULT_INSTALL_PATH or r"D:\CodeTools"
        return os.path.join(base_path, "Git")

    def _check_git_installed(self, package_id):
        """检查 Git 是否已安装。"""
        versions = WingetUtils.list_installed_versions(package_id)
        if versions:
            PrintUtils.print_success(f"检测到 Git 已安装，版本: {', '.join(versions)}")
            return True
        return False

    def _uninstall_git(self, package_id):
        """卸载已安装的 Git。"""
        PrintUtils.print_warning("警告: 此操作将卸载 Git for Windows")
        confirm = input("确定要继续卸载吗？[y/N]: ").strip().lower()
        if confirm not in ["y", "yes"]:
            PrintUtils.print_info("取消卸载")
            return False

        if WingetUtils.uninstall(package_id):
            PrintUtils.print_success("Git for Windows 卸载成功")
            return True

        PrintUtils.print_error("Git for Windows 卸载失败")
        return False

    def run(self):
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("Git for Windows 一键安装工具")
        PrintUtils.print_info("将优先使用默认安装根目录下的 Git 子目录")
        PrintUtils.print_info("=" * 60)

        package_id = "Git.Git"
        git_install_path = self._get_git_install_path()

        # 已安装时先给出“重装/卸载/退出”选项
        if self._check_git_installed(package_id):
            options = {
                1: "重新安装 Git for Windows",
                2: "卸载 Git for Windows",
                3: "退出",
            }
            code, _ = ChooseTask(options, "Git 已安装，请选择操作:").run()
            if code == 0 or code == 3:
                PrintUtils.print_info("退出")
                return True
            if code == 2:
                return self._uninstall_git(package_id)
            if code == 1:
                reinstall_confirm = input("重新安装前是否先卸载现有版本？[y/N]: ").strip().lower()
                if reinstall_confirm in ["y", "yes"] and not self._uninstall_git(package_id):
                    PrintUtils.print_warning("卸载未完成，已取消重新安装")
                    return False

        PrintUtils.print_info(f"目标安装路径(期望): {git_install_path}")
        PrintUtils.print_warning(
            "注意: Git.Git 是否使用 --location 取决于安装器，实际路径可能回退到默认目录"
        )

        ok = WingetUtils.install(
            package_id,
            custom_location=git_install_path,
            source="winget",
        )
        if not ok:
            PrintUtils.print_error("Git for Windows 安装失败")
            PrintUtils.print_warning(
                "建议先执行 `winget --version` 检查 winget 是否可用后重试"
            )
            return False

        PrintUtils.print_success("Git for Windows 安装完成")
        PrintUtils.print_info("可执行 `where git` 和 `git --version` 进行验证")
        return True
