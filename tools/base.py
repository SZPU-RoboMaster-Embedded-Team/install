# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import platform
import urllib.request
import urllib.error
from queue import Queue

# 启用 Windows 控制台颜色支持
if platform.system() == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

# 导入配置
try:
    # 尝试从父目录导入配置
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    WINGET_INSTALL_PATH = config.WINGET_INSTALL_PATH
except:
    # 如果配置文件不存在，使用默认值
    WINGET_INSTALL_PATH = r'D:\wingetApp'

# 检测是否有 yaml 模块
have_yaml_module = False
try:
    import yaml
    have_yaml_module = True
except:
    print('WARN: No Yaml Module!')

# Windows 平台检测
is_windows = platform.system() == 'Windows'
osarch = platform.machine().lower()
if osarch == 'amd64' or osarch == 'x86_64':
    osarch = 'amd64'
elif osarch == 'arm64' or osarch == 'aarch64':
    osarch = 'arm64'

osversion = platform.platform()


def check_admin():
    """检查是否有管理员权限（Windows）"""
    if not is_windows:
        return False
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


class ConfigHelper():
    """配置文件助手"""
    def __init__(self, record_file=None):
        self.record_input_queue = Queue()
        self.record_file = record_file
        if self.record_file is None:
            self.record_file = os.environ.get('FISH_INSTALL_CONFIG', "./fish_install.yaml")
        self.default_input_queue = self.get_default_queue(self.record_file)

    def record_input(self, item):
        self.record_input_queue.put(item)

    def gen_config_file(self):
        """生成配置文件"""
        config_yaml = {}
        chooses = []

        while self.record_input_queue.qsize() > 0:
            chooses.append(self.record_input_queue.get())

        config_yaml['chooses'] = chooses
        config_yaml['time'] = str(time.time())

        temp_path = os.path.join(os.environ.get('TEMP', '.'), 'fish_install_temp.yaml')
        target_path = os.path.join(os.environ.get('TEMP', '.'), 'fish_install.yaml')

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                if have_yaml_module:
                    yaml.dump(config_yaml, f, allow_unicode=True)

            if os.path.exists(target_path):
                print("检测到已存在的配置文件: {}".format(target_path))
                user_input = input("是否替换该文件？[y/N]: ")
                if user_input.lower() not in ['y', 'yes']:
                    print("取消替换，保留原配置文件")
                    os.remove(temp_path)
                    return
                os.remove(target_path)

            os.rename(temp_path, target_path)
            print("配置文件已保存至: {}".format(target_path))
        except Exception as e:
            print("配置文件生成过程中发生错误: {}".format(str(e)))
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_input_value(self):
        if self.default_input_queue.qsize() > 0:
            return self.default_input_queue.get()

    def record_choose(self, data):
        self.record_input_queue.put(data)

    def get_default_queue(self, param_file_path):
        """获取默认的配置"""
        config_data = None
        choose_queue = Queue()

        if not have_yaml_module:
            return choose_queue

        if not os.path.exists(param_file_path):
            return choose_queue

        with open(param_file_path, "r", encoding="utf-8") as f:
            config_data = f.read()

        if config_data is None:
            return choose_queue

        if hasattr(yaml, 'FullLoader'):
            config_yaml = yaml.load(config_data, Loader=yaml.FullLoader)
        else:
            config_yaml = yaml.load(config_data)

        for choose in config_yaml['chooses']:
            choose_queue.put(choose)

        return choose_queue


config_helper = ConfigHelper()


class PrintUtils:
    """打印工具类"""
    COLOR_RED = '\033[91m'
    COLOR_GREEN = '\033[92m'
    COLOR_YELLOW = '\033[93m'
    COLOR_BLUE = '\033[94m'
    COLOR_END = '\033[0m'

    @staticmethod
    def print_info(text):
        print(f"{PrintUtils.COLOR_BLUE}[INFO]{PrintUtils.COLOR_END} {text}")

    @staticmethod
    def print_success(text):
        print(f"{PrintUtils.COLOR_GREEN}[SUCCESS]{PrintUtils.COLOR_END} {text}")

    @staticmethod
    def print_error(text):
        print(f"{PrintUtils.COLOR_RED}[ERROR]{PrintUtils.COLOR_END} {text}")

    @staticmethod
    def print_warning(text):
        print(f"{PrintUtils.COLOR_YELLOW}[WARNING]{PrintUtils.COLOR_END} {text}")

    @staticmethod
    def print_delay(text, delay=0.01):
        """延迟打印"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()


class CmdTask:
    """命令执行任务"""
    def __init__(self, command, os_command=False, print_command=True):
        self.command = command
        self.os_command = os_command
        self.print_command = print_command

    def run(self):
        if self.print_command:
            PrintUtils.print_info(f"执行命令: {self.command}")

        try:
            if self.os_command:
                result = os.system(self.command)
                return result == 0
            else:
                result = subprocess.run(
                    self.command,
                    shell=True,
                    capture_output=False,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            PrintUtils.print_error(f"命令执行失败: {str(e)}")
            return False


class FileUtils:
    """文件操作工具"""
    @staticmethod
    def exists(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def write(file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            PrintUtils.print_error(f"写入文件失败: {str(e)}")
            return False

    @staticmethod
    def append(file_path, content):
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
            return True
        except Exception as e:
            PrintUtils.print_error(f"追加文件失败: {str(e)}")
            return False

    @staticmethod
    def read(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            PrintUtils.print_error(f"读取文件失败: {str(e)}")
            return None

    @staticmethod
    def download(url, save_path, show_progress=True):
        """下载文件"""
        try:
            PrintUtils.print_info(f"正在下载: {url}")

            def reporthook(count, block_size, total_size):
                if show_progress and total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    print(f"\r下载进度: {percent}%", end='', flush=True)

            urllib.request.urlretrieve(url, save_path, reporthook if show_progress else None)
            if show_progress:
                print()  # 换行
            PrintUtils.print_success(f"下载完成: {save_path}")
            return True
        except Exception as e:
            PrintUtils.print_error(f"下载失败: {str(e)}")
            return False


class WingetUtils:
    """Winget 包管理工具"""
    # 默认安装路径（从配置文件读取）
    DEFAULT_INSTALL_PATH = WINGET_INSTALL_PATH

    @staticmethod
    def check_winget():
        """检查 winget 是否可用"""
        try:
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    @staticmethod
    def install(package_id, accept_source_agreements=True, accept_package_agreements=True,
                custom_location=None, use_default_location=True, source='winget'):
        """安装软件包

        Args:
            package_id: 软件包 ID
            accept_source_agreements: 接受源协议
            accept_package_agreements: 接受软件包协议
            custom_location: 自定义安装路径（如果指定，会覆盖 use_default_location）
            use_default_location: 是否使用默认安装路径 D:\wingetApp
            source: 指定源（默认 'winget'，避免从其他源搜索导致的连接错误）
        """
        if not WingetUtils.check_winget():
            PrintUtils.print_error("Winget 不可用，请确保系统已安装 Windows 应用安装程序")
            return False

        cmd = f'winget install --id {package_id}'
        # 指定源，避免从多个源搜索导致的连接错误
        if source:
            cmd += f' --source {source}'
        if accept_source_agreements:
            cmd += ' --accept-source-agreements'
        if accept_package_agreements:
            cmd += ' --accept-package-agreements'

        # 确定安装路径
        install_location = None
        if custom_location:
            install_location = custom_location
        elif use_default_location:
            install_location = WingetUtils.DEFAULT_INSTALL_PATH

        # 添加安装路径参数
        if install_location:
            # 确保目录存在
            if not os.path.exists(install_location):
                try:
                    os.makedirs(install_location, exist_ok=True)
                    PrintUtils.print_info(f"创建安装目录: {install_location}")
                except Exception as e:
                    PrintUtils.print_warning(f"无法创建目录 {install_location}: {e}")

            cmd += f' --location "{install_location}"'
            PrintUtils.print_info(f"安装路径: {install_location}")

        return CmdTask(cmd).run()

    @staticmethod
    def search(keyword):
        """搜索软件包"""
        if not WingetUtils.check_winget():
            PrintUtils.print_error("Winget 不可用")
            return False

        return CmdTask(f'winget search {keyword}').run()

    @staticmethod
    def list_installed():
        """列出已安装的软件"""
        if not WingetUtils.check_winget():
            PrintUtils.print_error("Winget 不可用")
            return False

        return CmdTask('winget list').run()

    @staticmethod
    def uninstall(package_id, silent=False, all_versions=False, version=None):
        """卸载软件包

        Args:
            package_id: 软件包 ID
            silent: 是否静默卸载（跳过确认提示）
            all_versions: 是否卸载所有版本
            version: 指定要卸载的版本号（如果指定，会覆盖 all_versions）
        """
        if not WingetUtils.check_winget():
            PrintUtils.print_error("Winget 不可用，请确保系统已安装 Windows 应用安装程序")
            return False

        cmd = f'winget uninstall --id {package_id}'
        if version:
            cmd += f' --version {version}'
        elif all_versions:
            cmd += ' --all-versions'
        
        if silent:
            cmd += ' --silent'

        return CmdTask(cmd).run()

    @staticmethod
    def list_installed_versions(package_id):
        """列出已安装的包的所有版本
        
        Args:
            package_id: 软件包 ID
            
        Returns:
            list: 版本列表，如果没有找到则返回空列表
        """
        if not WingetUtils.check_winget():
            PrintUtils.print_error("Winget 不可用")
            return []

        try:
            # 使用 bytes 模式捕获输出，然后手动解码以处理编码问题
            result = subprocess.run(
                ['winget', 'list', '--id', package_id],
                capture_output=True,
                text=False  # 先获取 bytes
            )
            
            if result.returncode != 0:
                return []
            
            # 安全地解码输出，处理编码问题
            if result.stdout is None:
                return []
            
            # 尝试多种编码方式
            output_text = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1']:
                try:
                    output_text = result.stdout.decode(encoding, errors='replace')
                    break
                except (UnicodeDecodeError, AttributeError):
                    continue
            
            if output_text is None:
                # 如果所有编码都失败，使用 errors='replace' 强制解码
                try:
                    output_text = result.stdout.decode('utf-8', errors='replace')
                except:
                    return []
            
            versions = []
            lines = output_text.split('\n')
            found_header = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 查找表头行（包含"名称"、"ID"、"版本"等关键词）
                if '名称' in line or ('ID' in line and ('版本' in line or 'Version' in line)):
                    found_header = True
                    continue
                
                # 跳过分隔线
                if line.startswith('-') or line.startswith('='):
                    continue
                
                # 查找包含包 ID 的数据行
                if package_id in line and found_header:
                    parts = line.split()
                    # winget list 输出格式通常是: 名称 ID 版本 源
                    # 例如: MSYS2 MSYS2.MSYS2 20251213 winget
                    try:
                        for i, part in enumerate(parts):
                            if part == package_id and i + 1 < len(parts):
                                version = parts[i + 1]
                                # 验证版本号格式，排除源名称如 "winget", "msstore" 等
                                if version and version not in ['winget', 'msstore', 'chocolatey']:
                                    # 检查是否为版本号格式（包含数字）
                                    if any(c.isdigit() for c in version):
                                        if version not in versions:
                                            versions.append(version)
                                    break
                    except (IndexError, ValueError):
                        continue
            
            return versions
        except Exception as e:
            PrintUtils.print_warning(f"列出已安装版本时出错: {str(e)}")
            # 如果解析失败，返回空列表，让调用者尝试直接卸载
            return []


class EnvUtils:
    """环境变量配置工具（通用工具类）"""
    
    @staticmethod
    def add_to_system_path(paths, skip_if_not_admin=True):
        """添加路径到系统PATH环境变量
        
        Args:
            paths: 路径列表（字符串列表）
            skip_if_not_admin: 如果没有管理员权限是否跳过
            
        Returns:
            bool: 是否成功
        """
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False
        
        if not check_admin():
            if skip_if_not_admin:
                PrintUtils.print_warning("需要管理员权限来修改系统环境变量")
                PrintUtils.print_info("将尝试添加到用户环境变量")
                return EnvUtils.add_to_user_path(paths)
            else:
                PrintUtils.print_error("需要管理员权限")
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
                path_abs = os.path.abspath(path)
                if path_abs not in path_list:
                    path_list.append(path_abs)
                    added_paths.append(path_abs)
            
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
                
                PrintUtils.print_success("已添加以下路径到系统PATH:")
                for p in added_paths:
                    PrintUtils.print_info(f"  - {p}")
                PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
                return True
            else:
                winreg.CloseKey(key)
                PrintUtils.print_info("所有路径已存在于系统PATH中")
                return True
                
        except Exception as e:
            PrintUtils.print_error(f"修改系统环境变量失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def add_to_user_path(paths):
        """添加路径到用户PATH环境变量（不需要管理员权限）
        
        Args:
            paths: 路径列表（字符串列表）
            
        Returns:
            bool: 是否成功
        """
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False
        
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
                path_abs = os.path.abspath(path)
                if path_abs not in path_list:
                    path_list.append(path_abs)
                    added_paths.append(path_abs)
            
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
                
                PrintUtils.print_success("已添加以下路径到用户PATH:")
                for p in added_paths:
                    PrintUtils.print_info(f"  - {p}")
                PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
                return True
            else:
                winreg.CloseKey(key)
                PrintUtils.print_info("所有路径已存在于用户PATH中")
                return True
                
        except Exception as e:
            PrintUtils.print_error(f"修改用户环境变量失败: {e}")
            return False
    
    @staticmethod
    def configure_path_environment(paths, skip_if_not_admin=True):
        """配置PATH环境变量（通用方法）
        
        Args:
            paths: 需要添加的路径列表（字符串列表）
            skip_if_not_admin: 如果没有管理员权限是否跳过（False时要求管理员权限）
            
        Returns:
            bool: 是否成功
        """
        if not paths:
            PrintUtils.print_warning("路径列表为空")
            return False
        
        # 尝试添加到系统PATH（需要管理员权限）
        if check_admin():
            return EnvUtils.add_to_system_path(paths, skip_if_not_admin=False)
        else:
            # 如果没有管理员权限，添加到用户PATH
            if skip_if_not_admin:
                PrintUtils.print_warning("没有管理员权限，将添加到用户PATH")
                return EnvUtils.add_to_user_path(paths)
            else:
                PrintUtils.print_error("需要管理员权限")
                return False


class ChooseTask:
    """选择任务"""
    def __init__(self, options, tips="请选择:"):
        self.options = options
        self.tips = tips

    def run(self):
        """运行选择任务"""
        # 检查是否有默认配置
        default_value = config_helper.get_input_value()
        if default_value is not None:
            PrintUtils.print_info(f"使用配置文件中的选项: {default_value['choose']}")
            return default_value['choose'], self.options.get(default_value['choose'])

        print(f"\n{self.tips}")
        for key, value in self.options.items():
            print(f"  {key}. {value}")

        while True:
            try:
                choice = input("\n请输入选项编号: ").strip()
                choice_num = int(choice)
                if choice_num in self.options:
                    # 记录选择
                    config_helper.record_choose({
                        'choose': choice_num,
                        'desc': self.options[choice_num]
                    })
                    return choice_num, self.options[choice_num]
                else:
                    PrintUtils.print_warning("无效的选项，请重新输入")
            except ValueError:
                PrintUtils.print_warning("请输入数字")
            except KeyboardInterrupt:
                print("\n\n用户取消操作")
                return 0, None


class ChooseWithCategoriesTask:
    """带分类的选择任务"""
    def __init__(self, tool_categories, tips="请选择:", categories=None):
        self.tool_categories = tool_categories
        self.tips = tips
        self.categories = categories or {}

    def run(self):
        """运行选择任务"""
        # 检查是否有默认配置
        default_value = config_helper.get_input_value()
        if default_value is not None:
            PrintUtils.print_info(f"使用配置文件中的选项: {default_value['choose']}")
            return default_value['choose'], None

        print(f"\n{self.tips}")
        for category_id, tools in self.tool_categories.items():
            category_name = self.categories.get(category_id, f"分类 {category_id}")
            print(f"\n=== {category_name} ===")
            for tool_id, tool_info in tools.items():
                print(f"  {tool_id}. {tool_info['tip']}")

        while True:
            try:
                choice = input("\n请输入选项编号 (0 退出): ").strip()
                choice_num = int(choice)

                if choice_num == 0:
                    return 0, None

                # 查找工具
                for tools in self.tool_categories.values():
                    if choice_num in tools:
                        # 记录选择
                        config_helper.record_choose({
                            'choose': choice_num,
                            'desc': tools[choice_num]['tip']
                        })
                        return choice_num, tools[choice_num]

                PrintUtils.print_warning("无效的选项，请重新输入")
            except ValueError:
                PrintUtils.print_warning("请输入数字")
            except KeyboardInterrupt:
                print("\n\n用户取消操作")
                return 0, None


class BaseTool:
    """工具基类"""
    TYPE_INSTALL = 0
    TYPE_CONFIG = 1

    def __init__(self):
        self.name = "基础工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = "未知"

    def run(self):
        """运行工具"""
        raise NotImplementedError("子类必须实现 run 方法")


def run_tool_file(tool_path):
    """运行工具文件"""
    try:
        # 将路径转换为模块路径
        module_path = tool_path.replace('/', '.').replace('\\', '.').replace('.py', '')

        # 动态导入模块
        import importlib
        module = importlib.import_module(module_path)

        # 创建工具实例并运行
        tool = module.Tool()
        PrintUtils.print_info(f"开始运行工具: {tool.name}")
        tool.run()
        PrintUtils.print_success(f"工具运行完成: {tool.name}")
        return True
    except Exception as e:
        PrintUtils.print_error(f"运行工具失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
