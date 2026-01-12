# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, EnvUtils, check_admin
from .base import osversion, osarch
import os
import sys
import json
import re
import zipfile
import urllib.request
import urllib.error

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 ARM GCC 工具链"
        self.type = BaseTool.TYPE_INSTALL
        self.author = '小鱼'
        
        # 从配置文件获取安装目录
        try:
            # 尝试从父目录导入配置
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            import config
            if hasattr(config, 'ARM_GCC_INSTALL_DIR'):
                self.install_dir = config.ARM_GCC_INSTALL_DIR
            else:
                # 如果配置文件中没有，使用默认值
                self.install_dir = r'D:\CodeTools\Compiler'
        except:
            # 如果导入失败，使用默认值
            self.install_dir = r'D:\CodeTools\Compiler'
        
        # GitHub API 端点
        self.github_api_url = 'https://api.github.com/repos/carlosperate/arm-none-eabi-gcc-action/releases/latest'
        
        # 后备版本（如果无法从 GitHub 获取）
        self.fallback_version = '15.2.Rel1'

    def get_latest_version_from_github(self):
        """使用 GitHub API 获取最新 release，并从 release notes 中解析工具链版本号
        
        Returns:
            str: 工具链版本号，如果获取失败返回 None
        """
        try:
            PrintUtils.print_info("正在从 GitHub 获取最新版本信息...")
            
            # 创建请求
            req = urllib.request.Request(self.github_api_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # 获取 release notes
                body = data.get('body', '')
                tag_name = data.get('tag_name', '')
                
                PrintUtils.print_info(f"GitHub Release: {tag_name}")
                
                # 尝试从 release notes 中解析版本号
                # 格式可能是: "Add `15.2.Rel1`" 或 "15.2.Rel1" 等
                # 匹配类似 15.2.Rel1, 14.3.Rel1, 12.3.Rel1 等格式
                version_patterns = [
                    r'`?(\d+\.\d+\.Rel\d+)`?',  # 匹配 `15.2.Rel1` 或 15.2.Rel1
                    r'(\d+\.\d+\.Rel\d+)',      # 匹配 15.2.Rel1
                    r'(\d+\.\d+-\d{4}-q\d)',    # 匹配旧格式如 10-2020-q4
                ]
                
                for pattern in version_patterns:
                    match = re.search(pattern, body, re.IGNORECASE)
                    if match:
                        version = match.group(1)
                        PrintUtils.print_success(f"解析到工具链版本: {version}")
                        return version
                
                # 如果无法从 body 中解析，尝试从 tag_name 或其他字段获取
                PrintUtils.print_warning("无法从 release notes 中解析版本号")
                return None
                
        except urllib.error.URLError as e:
            PrintUtils.print_warning(f"无法连接到 GitHub API: {e}")
            return None
        except json.JSONDecodeError as e:
            PrintUtils.print_warning(f"解析 GitHub API 响应失败: {e}")
            return None
        except Exception as e:
            PrintUtils.print_warning(f"获取版本信息时发生错误: {e}")
            return None

    def get_download_url(self, version):
        """构建 Arm 官方的下载 URL
        
        Args:
            version: 工具链版本号（如 '15.2.Rel1'）
            
        Returns:
            str: 下载 URL
        """
        # Windows x86_64 版本的下载 URL 格式
        # https://developer.arm.com/-/media/Files/downloads/gnu/{version}/binrel/arm-gnu-toolchain-{version}-mingw-w64-i686-arm-none-eabi.zip
        base_url = 'https://developer.arm.com/-/media/Files/downloads/gnu'
        filename = f'arm-gnu-toolchain-{version}-mingw-w64-i686-arm-none-eabi.zip'
        url = f'{base_url}/{version}/binrel/{filename}'
        return url

    def download_toolchain(self, version, target_dir):
        """下载工具链 zip 文件
        
        Args:
            version: 工具链版本号
            target_dir: 目标目录
            
        Returns:
            str: 下载的文件路径，如果失败返回 None
        """
        try:
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 构建下载 URL
            download_url = self.get_download_url(version)
            PrintUtils.print_info(f"下载 URL: {download_url}")
            
            # 临时文件路径
            temp_dir = os.environ.get('TEMP', '.')
            zip_filename = f'arm-gnu-toolchain-{version}-mingw-w64-i686-arm-none-eabi.zip'
            zip_path = os.path.join(temp_dir, zip_filename)
            
            # 下载文件
            if not FileUtils.download(download_url, zip_path):
                return None
            
            return zip_path
            
        except Exception as e:
            PrintUtils.print_error(f"下载工具链时发生错误: {e}")
            return None

    def extract_toolchain(self, zip_path, target_dir):
        """使用 zipfile 模块解压工具链到目标目录
        
        Args:
            zip_path: zip 文件路径
            target_dir: 目标目录（D:\CodeTools\Compiler）
            
        Returns:
            str: 解压后的工具链目录路径，如果失败返回 None
        """
        try:
            # 创建 arm-none-eabi-gcc 子目录
            armgcc_dir = os.path.join(target_dir, 'arm-none-eabi-gcc')
            PrintUtils.print_info(f"正在解压到: {armgcc_dir}")
            
            # 确保目标目录存在
            os.makedirs(armgcc_dir, exist_ok=True)
            
            # 打开 zip 文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取所有文件列表
                file_list = zip_ref.namelist()
                
                # 查找根目录（通常是第一个目录）
                root_dir = None
                for name in file_list:
                    if '/' in name:
                        root_dir = name.split('/')[0]
                        break
                    elif '\\' in name:
                        root_dir = name.split('\\')[0]
                        break
                
                if not root_dir:
                    PrintUtils.print_error("无法确定压缩包的根目录")
                    return None
                
                # 解压所有文件到 arm-none-eabi-gcc 目录
                zip_ref.extractall(armgcc_dir)
                
                # 返回解压后的完整路径
                extracted_path = os.path.join(armgcc_dir, root_dir)
                PrintUtils.print_success(f"解压完成: {extracted_path}")
                
                return extracted_path
                
        except zipfile.BadZipFile:
            PrintUtils.print_error("无效的 zip 文件")
            return None
        except Exception as e:
            PrintUtils.print_error(f"解压工具链时发生错误: {e}")
            return None

    def get_bin_path(self, toolchain_dir):
        """获取 bin 目录的完整路径
        
        Args:
            toolchain_dir: 工具链根目录
            
        Returns:
            str: bin 目录路径，如果不存在返回 None
        """
        bin_path = os.path.join(toolchain_dir, 'bin')
        if os.path.exists(bin_path):
            return bin_path
        return None

    def check_installed(self):
        """检查是否已安装（通过检查 bin 目录是否存在）
        
        Returns:
            tuple: (是否已安装, bin目录路径)
        """
        # 检查安装目录下是否有 arm-none-eabi-gcc 目录
        armgcc_dir = os.path.join(self.install_dir, 'arm-none-eabi-gcc')
        if not os.path.exists(armgcc_dir):
            return False, None
        
        # 在 arm-none-eabi-gcc 目录下查找工具链目录
        for item in os.listdir(armgcc_dir):
            item_path = os.path.join(armgcc_dir, item)
            if os.path.isdir(item_path):
                # 检查是否是工具链目录（通常包含 arm-gnu-toolchain）
                if 'arm-gnu-toolchain' in item.lower():
                    bin_path = self.get_bin_path(item_path)
                    if bin_path and os.path.exists(bin_path):
                        # 检查 bin 目录中是否有 arm-none-eabi-gcc.exe
                        gcc_exe = os.path.join(bin_path, 'arm-none-eabi-gcc.exe')
                        if os.path.exists(gcc_exe):
                            return True, bin_path
        
        return False, None

    def run(self):
        """运行安装流程"""
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("ARM GCC 工具链一键安装工具")
        PrintUtils.print_info("安装 Arm GNU Embedded Toolchain (arm-none-eabi-gcc)")
        PrintUtils.print_info("=" * 60)
        PrintUtils.print_info("")

        # 检查是否已安装
        is_installed, bin_path = self.check_installed()
        if is_installed:
            PrintUtils.print_success(f"检测到 ARM GCC 工具链已安装在: {bin_path}")
            PrintUtils.print_info("")
            choice = input("是否重新安装？[y/N]: ").strip().lower()
            if choice not in ['y', 'yes']:
                PrintUtils.print_info("取消安装")
                return

        # 获取最新版本
        version = self.get_latest_version_from_github()
        if not version:
            PrintUtils.print_warning(f"无法从 GitHub 获取版本，使用后备版本: {self.fallback_version}")
            version = self.fallback_version
        else:
            PrintUtils.print_success(f"将安装版本: {version}")

        PrintUtils.print_info("")

        # 下载工具链
        PrintUtils.print_info("开始下载工具链...")
        zip_path = self.download_toolchain(version, self.install_dir)
        if not zip_path:
            PrintUtils.print_error("下载失败")
            return

        PrintUtils.print_info("")

        # 解压工具链
        PrintUtils.print_info("开始解压工具链...")
        toolchain_dir = self.extract_toolchain(zip_path, self.install_dir)
        if not toolchain_dir:
            PrintUtils.print_error("解压失败")
            # 清理下载的文件
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            except:
                pass
            return

        # 获取 bin 目录路径（直接使用 arm-none-eabi-gcc\bin）
        armgcc_dir = os.path.join(self.install_dir, 'arm-none-eabi-gcc')
        bin_path = os.path.join(armgcc_dir, 'bin')
        
        # 验证 bin 目录是否存在
        if not os.path.exists(bin_path):
            PrintUtils.print_error(f"未找到 bin 目录: {bin_path}")
            return

        PrintUtils.print_info("")

        # 添加到环境变量（只添加这一个路径）
        bin_path_abs = os.path.abspath(bin_path)
        PrintUtils.print_info(f"正在添加以下路径到系统 PATH 环境变量:")
        PrintUtils.print_info(f"  {bin_path_abs}")
        if EnvUtils.add_to_system_path([bin_path_abs], skip_if_not_admin=True):
            PrintUtils.print_success("已添加到 PATH 环境变量")
        else:
            PrintUtils.print_warning("添加到 PATH 环境变量失败，请手动添加")
            PrintUtils.print_info(f"请手动将以下路径添加到 PATH: {bin_path}")

        PrintUtils.print_info("")

        # 清理临时文件
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                PrintUtils.print_info("已清理临时文件")
        except:
            pass

        # 安装完成
        PrintUtils.print_success("=" * 60)
        PrintUtils.print_success("安装完成!")
        PrintUtils.print_info("")
        PrintUtils.print_info("使用说明:")
        PrintUtils.print_info("  1. 请重新打开命令行窗口以使环境变量生效")
        PrintUtils.print_info("  2. 运行以下命令验证安装:")
        PrintUtils.print_info("     arm-none-eabi-gcc --version")
        PrintUtils.print_info("")
        PrintUtils.print_info(f"安装路径: {toolchain_dir}")
        PrintUtils.print_info(f"Bin 目录: {bin_path}")
        PrintUtils.print_success("=" * 60)

