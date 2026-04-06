# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import platform
import re
import threading
import socket
import ssl
import urllib.request
import urllib.error
import shutil
import tempfile

# 启用 Windows 控制台颜色支持
if platform.system() == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

def _ensure_persistent_config():
    """确保 config.py 从可持久化位置加载（避免 EXE onefile 写入 _MEI 临时目录丢失）。"""
    # 源码运行：默认从项目根目录读取
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if platform.system() != "Windows":
        return

    # EXE/Windows：优先使用 LOCALAPPDATA\fishros_install\config.py
    try:
        local_appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not local_appdata:
            return

        cfg_dir = os.path.join(local_appdata, "fishros_install")
        cfg_path = os.path.join(cfg_dir, "config.py")
        os.makedirs(cfg_dir, exist_ok=True)

        # 不存在就创建：优先拷贝打包内置的 config.py；否则拷贝项目根目录的 config.py；再否则生成最小模板
        if not os.path.exists(cfg_path):
            bundled = None
            if getattr(sys, "frozen", False):
                meipass = getattr(sys, "_MEIPASS", None)
                if meipass:
                    candidate = os.path.join(meipass, "config.py")
                    if os.path.exists(candidate):
                        bundled = candidate

            root_cfg = os.path.join(project_root, "config.py")
            if bundled and os.path.exists(bundled):
                shutil.copyfile(bundled, cfg_path)
            elif os.path.exists(root_cfg):
                shutil.copyfile(root_cfg, cfg_path)
            else:
                FileUtils.write(
                    cfg_path,
                    "# -*- coding: utf-8 -*-\n"
                    "WINGET_INSTALL_PATH = r'D:\\\\CodeTools'\n"
                    "MSYS2_PATHS = [r'D:\\\\CodeTools\\\\msys64', r'D:\\\\CodeTools', r'C:\\\\msys64', r'C:\\\\msys32']\n"
                    "ARM_GCC_INSTALL_DIR = r'D:\\\\CodeTools\\\\Compiler'\n"
                )

        if cfg_dir not in sys.path:
            sys.path.insert(0, cfg_dir)
    except Exception:
        return


# 导入配置
_ensure_persistent_config()
try:
    import config
    WINGET_INSTALL_PATH = getattr(config, "WINGET_INSTALL_PATH", r"D:\CodeTools")
except Exception:
    # 如果配置文件不存在，使用默认值
    WINGET_INSTALL_PATH = r'D:\CodeTools'

# 如果配置里的默认目录不存在，自动回退到 D:\CodeTools（按用户期望）
try:
    if not WINGET_INSTALL_PATH or not os.path.isdir(WINGET_INSTALL_PATH):
        WINGET_INSTALL_PATH = r"D:\CodeTools"
except Exception:
    WINGET_INSTALL_PATH = r"D:\CodeTools"


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
    def _get_network_status_brief(timeout_sec=3):
        """获取简短网络状态，用于长时间无输出时的用户反馈（Windows/通用）。

        Returns:
            str: 状态字符串（尽量短）
        """
        host = "www.msftconnecttest.com"
        http_url = "http://www.msftconnecttest.com/connecttest.txt"
        https_url = "https://www.msftconnecttest.com/connecttest.txt"

        dns_ok = False
        http_ok = False
        https_ok = False
        dns_err = ""
        http_err = ""
        https_err = ""
        http_ms = None
        https_ms = None

        try:
            socket.gethostbyname(host)
            dns_ok = True
        except Exception as e:
            dns_err = str(e)

        # 先用 HTTP 探测连通性，避免 HTTPS 证书问题造成“误报无网”
        if dns_ok:
            try:
                start = time.time()
                req = urllib.request.Request(http_url, method="GET")
                with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                    _ = resp.read(64)  # 读少量即可确认连通
                http_ms = int((time.time() - start) * 1000)
                http_ok = True
            except Exception as e:
                http_err = str(e)

        # 再尝试 HTTPS（如果证书校验失败，提示“可能被代理/证书异常”，但不把它当成断网）
        if dns_ok:
            try:
                start = time.time()
                req = urllib.request.Request(https_url, method="GET")
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    _ = resp.read(64)
                https_ms = int((time.time() - start) * 1000)
                https_ok = True
            except Exception as e:
                https_err = str(e)

        parts = []
        if dns_ok:
            parts.append("DNS: ok")
        else:
            parts.append(f"DNS: fail ({dns_err})" if dns_err else "DNS: fail")

        if http_ok:
            parts.append(f"HTTP: ok ({http_ms}ms)" if http_ms is not None else "HTTP: ok")
        else:
            if not dns_ok:
                parts.append("HTTP: skip")
            else:
                parts.append(f"HTTP: fail ({http_err})" if http_err else "HTTP: fail")

        if https_ok:
            parts.append(f"HTTPS: ok ({https_ms}ms)" if https_ms is not None else "HTTPS: ok")
        else:
            if not dns_ok:
                parts.append("HTTPS: skip")
            else:
                # 常见：被代理/安全软件拦截导致证书校验失败
                lower = (https_err or "").lower()
                if "certificate_verify_failed" in lower or "hostname mismatch" in lower:
                    parts.append("HTTPS: cert issue (可能被代理/证书异常)")
                else:
                    parts.append(f"HTTPS: fail ({https_err})" if https_err else "HTTPS: fail")

        return ", ".join(parts)

    @staticmethod
    def _start_network_status_thread(stop_event, interval_sec=10):
        """后台周期打印网络状态，直到 stop_event 被 set()."""
        def _worker():
            # 立即打印一次，给用户“正在进行”的反馈
            try:
                PrintUtils.print_info(f"网络状态: {WingetUtils._get_network_status_brief()}")
            except Exception:
                # 任何异常都不影响主流程
                pass

            while not stop_event.wait(interval_sec):
                try:
                    PrintUtils.print_info(f"网络状态: {WingetUtils._get_network_status_brief()}")
                except Exception:
                    pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return t

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

        PrintUtils.print_info("即将执行 winget 安装命令")
        PrintUtils.print_info(f"命令: {cmd}")
        PrintUtils.print_info("执行后可能短时间无输出，这是下载或安装程序初始化的正常现象")

        try:
            PrintUtils.print_info("正在启动 winget 安装进程...")
            # winget 安装阶段经常长时间无输出，这里周期性展示网络状态，缓解用户焦虑
            stop_event = threading.Event()
            net_thread = WingetUtils._start_network_status_thread(stop_event, interval_sec=10)
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=False
            )
            stop_event.set()
            try:
                net_thread.join(timeout=1)
            except Exception:
                pass
            PrintUtils.print_info(f"winget 安装进程结束，返回码: {result.returncode}")

            def _decode_output(raw_bytes):
                if not raw_bytes:
                    return ""
                for encoding in ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1']:
                    try:
                        return raw_bytes.decode(encoding, errors='replace')
                    except Exception:
                        continue
                return raw_bytes.decode('utf-8', errors='replace')

            stdout_text = _decode_output(result.stdout)
            stderr_text = _decode_output(result.stderr)

            if stdout_text.strip():
                print(stdout_text, end="" if stdout_text.endswith("\n") else "\n")
            if stderr_text.strip():
                print(stderr_text, end="" if stderr_text.endswith("\n") else "\n")

            if result.returncode == 0:
                PrintUtils.print_success(f"{package_id} 安装命令执行成功")
                return True

            # winget 已安装且无可升级版本时可能返回非 0，按成功处理
            combined = f"{stdout_text}\n{stderr_text}".lower()
            no_upgrade_markers = [
                "找到已安装的现有包",
                "找不到可用的升级",
                "没有可用的较新的包版本",
                "already installed",
                "no available upgrade",
                "no applicable upgrade found",
            ]
            if any(marker in combined for marker in no_upgrade_markers):
                installed_versions = WingetUtils.list_installed_versions(package_id)
                if installed_versions:
                    PrintUtils.print_info(
                        f"{package_id} 已安装（无可升级版本），将继续后续流程"
                    )
                    return True

            PrintUtils.print_error(f"winget install 返回非 0: {result.returncode}")
            PrintUtils.print_warning("可能原因: 网络连接异常、源访问失败、安装器权限限制或包状态异常")
            PrintUtils.print_warning("建议: 执行 `winget source list` 和 `winget list --id MSYS2.MSYS2` 排查")
            PrintUtils.print_warning("建议: 若持续失败，可切换为手动下载安装流程")
            return False
        except Exception as e:
            try:
                stop_event.set()
            except Exception:
                pass
            PrintUtils.print_error(f"执行 winget install 失败: {e}")
            PrintUtils.print_warning("建议: 先确认 winget 可用，再检查系统策略或安全软件是否拦截")
            return False

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
    def _normalize_path_for_compare(p):
        """用于 PATH 条目对比的规范化（Windows 大小写不敏感）。"""
        if p is None:
            return ""
        try:
            # 不强制要求存在；卸载时目录可能已被删除，但仍需从 PATH 移除
            p2 = os.path.expandvars(str(p).strip().strip('"').strip("'"))
            p2 = os.path.abspath(os.path.normpath(p2))
            if is_windows:
                p2 = os.path.normcase(p2)
            return p2
        except Exception:
            return str(p).strip()

    @staticmethod
    def _dedupe_keep_order(items):
        seen = set()
        out = []
        for x in items:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    @staticmethod
    def _split_path_value(path_value):
        if not path_value:
            return []
        return [p.strip() for p in str(path_value).split(os.pathsep) if p and p.strip()]

    @staticmethod
    def _join_path_value(path_list):
        # 过滤空串并去重（保持顺序）
        cleaned = [p.strip() for p in path_list if p and str(p).strip()]
        cleaned = EnvUtils._dedupe_keep_order(cleaned)
        return os.pathsep.join(cleaned)

    @staticmethod
    def get_system_path():
        """读取系统 PATH（HKLM）。返回 (path_str, reg_type)；失败返回 ("", None)。"""
        if not is_windows:
            return "", None
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_READ
            )
            try:
                v, t = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                v, t = "", None
            winreg.CloseKey(key)
            return v or "", t
        except Exception:
            return "", None

    @staticmethod
    def get_user_path():
        """读取用户 PATH（HKCU）。返回 (path_str, reg_type)；失败返回 ("", None)。"""
        if not is_windows:
            return "", None
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_READ
            )
            try:
                v, t = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                v, t = "", None
            winreg.CloseKey(key)
            return v or "", t
        except Exception:
            return "", None

    @staticmethod
    def delete_system_env_var(name):
        """删除系统级环境变量（HKLM）。不存在则视为成功。"""
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False
        if not check_admin():
            PrintUtils.print_error("需要管理员权限来修改系统环境变量")
            return False
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            try:
                winreg.DeleteValue(key, name)
                PrintUtils.print_success(f"已删除系统环境变量: {name}")
            except FileNotFoundError:
                # 不存在也算成功
                PrintUtils.print_info(f"系统环境变量不存在，无需删除: {name}")
            finally:
                winreg.CloseKey(key)
            EnvUtils._broadcast_environment_change()
            PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
            return True
        except Exception as e:
            PrintUtils.print_error(f"删除系统环境变量失败: {e}")
            return False

    @staticmethod
    def remove_from_system_path(paths, skip_if_not_admin=True):
        """从系统 PATH 中移除指定路径条目（精确匹配规范化后的路径）。"""
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False

        if not check_admin():
            if skip_if_not_admin:
                PrintUtils.print_warning("需要管理员权限来修改系统环境变量")
                PrintUtils.print_info("将尝试从用户 PATH 中移除")
                return EnvUtils.remove_from_user_path(paths)
            PrintUtils.print_error("需要管理员权限")
            return False

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            try:
                current_path, reg_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path, reg_type = "", winreg.REG_EXPAND_SZ

            path_list = EnvUtils._split_path_value(current_path)
            if not path_list:
                winreg.CloseKey(key)
                PrintUtils.print_info("系统 PATH 为空，无需移除")
                return True

            target_norms = set(EnvUtils._normalize_path_for_compare(p) for p in (paths or []))
            removed = []
            kept = []
            for p in path_list:
                if EnvUtils._normalize_path_for_compare(p) in target_norms:
                    removed.append(p)
                else:
                    kept.append(p)

            new_path = EnvUtils._join_path_value(kept)
            # 始终写回（即便 removed 为空也可做去重/清理，但这里保持稳妥仅在变化时写）
            if removed or new_path != EnvUtils._join_path_value(path_list):
                winreg.SetValueEx(
                    key,
                    "Path",
                    0,
                    reg_type if reg_type is not None else winreg.REG_EXPAND_SZ,
                    new_path
                )
                EnvUtils._broadcast_environment_change()

            winreg.CloseKey(key)

            if removed:
                PrintUtils.print_success("已从系统 PATH 移除以下路径:")
                for p in removed:
                    PrintUtils.print_info(f"  - {p}")
                PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
            else:
                PrintUtils.print_info("系统 PATH 中未找到需要移除的路径")
            return True
        except Exception as e:
            PrintUtils.print_error(f"修改系统环境变量失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def remove_from_user_path(paths):
        """从用户 PATH 中移除指定路径条目（精确匹配规范化后的路径）。"""
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                "Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            try:
                current_path, reg_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path, reg_type = "", winreg.REG_EXPAND_SZ

            path_list = EnvUtils._split_path_value(current_path)
            if not path_list:
                winreg.CloseKey(key)
                PrintUtils.print_info("用户 PATH 为空，无需移除")
                return True

            target_norms = set(EnvUtils._normalize_path_for_compare(p) for p in (paths or []))
            removed = []
            kept = []
            for p in path_list:
                if EnvUtils._normalize_path_for_compare(p) in target_norms:
                    removed.append(p)
                else:
                    kept.append(p)

            new_path = EnvUtils._join_path_value(kept)
            if removed or new_path != EnvUtils._join_path_value(path_list):
                winreg.SetValueEx(
                    key,
                    "Path",
                    0,
                    reg_type if reg_type is not None else winreg.REG_EXPAND_SZ,
                    new_path
                )
                EnvUtils._broadcast_environment_change()

            winreg.CloseKey(key)

            if removed:
                PrintUtils.print_success("已从用户 PATH 移除以下路径:")
                for p in removed:
                    PrintUtils.print_info(f"  - {p}")
                PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
            else:
                PrintUtils.print_info("用户 PATH 中未找到需要移除的路径")
            return True
        except Exception as e:
            PrintUtils.print_error(f"修改用户环境变量失败: {e}")
            return False

    @staticmethod
    def remove_from_path_environment(paths, prefer_system=True):
        """通用卸载入口：优先移除系统 PATH；同时也尝试移除用户 PATH（兼容历史写入）。"""
        if not paths:
            PrintUtils.print_warning("路径列表为空")
            return False

        ok = True
        if prefer_system:
            ok = EnvUtils.remove_from_system_path(paths, skip_if_not_admin=True) and ok
            # 兼容：可能之前写入到了用户 PATH
            ok = EnvUtils.remove_from_user_path(paths) and ok
        else:
            ok = EnvUtils.remove_from_user_path(paths) and ok
            # 兼容：可能之前写入到了系统 PATH
            ok = EnvUtils.remove_from_system_path(paths, skip_if_not_admin=True) and ok
        return ok

    @staticmethod
    def _broadcast_environment_change():
        """广播环境变量更改消息（带超时，避免 SendMessageW 广播卡死）"""
        if not is_windows:
            return
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002

            # SendMessageTimeoutW 比 SendMessageW 更安全：遇到无响应窗口不会无限等待
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                2000,  # 2s timeout
                None
            )
        except Exception:
            # 广播失败不影响 PATH 写入生效（新开的终端仍会读取到注册表）
            pass
    
    @staticmethod
    def set_system_env_var(name, value):
        """设置系统级环境变量 NAME=VALUE
        """
        if not is_windows:
            PrintUtils.print_warning("环境变量配置仅支持 Windows 平台")
            return False
        
        if not check_admin():
            PrintUtils.print_error("需要管理员权限来修改系统环境变量")
            return False
        
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, str(value))
            winreg.CloseKey(key)
            EnvUtils._broadcast_environment_change()
            PrintUtils.print_success(f"已设置系统环境变量: {name}={value}")
            PrintUtils.print_warning("请重新打开命令行窗口以使环境变量生效")
            return True
        except Exception as e:
            PrintUtils.print_error(f"设置系统环境变量失败: {e}")
            return False
    
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

                # 广播环境变量更改消息（带超时，避免卡死）
                EnvUtils._broadcast_environment_change()
                
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

                # 广播环境变量更改消息（带超时，避免卡死）
                EnvUtils._broadcast_environment_change()
                
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
        """配置 PATH 环境变量（通用方法）
        
        Args:
            paths: 需要添加的路径列表（字符串列表）
            skip_if_not_admin: 如果没有管理员权限是否跳过（False时要求管理员权限）
            
        Returns:
            bool: 是否成功

        Notes:
            - 安装写入 PATH 使用本方法；卸载请使用 `remove_from_path_environment()` 做对称清理。
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
        print(f"\n{self.tips}")
        for key, value in self.options.items():
            print(f"  {key}. {value}")

        while True:
            try:
                choice = input("\n请输入选项编号: ").strip()
                choice_num = int(choice)
                if choice_num in self.options:
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
                        return choice_num, tools[choice_num]

                PrintUtils.print_warning("无效的选项，请重新输入")
            except ValueError:
                PrintUtils.print_warning("请输入数字")
            except KeyboardInterrupt:
                print("\n\n用户取消操作")
                return 0, None


class ConfigUtils:
    """配置文件工具类"""

    @staticmethod
    def _to_raw_string(path):
        """将路径安全转换为 Python 原始字符串字面量内容"""
        return path.replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def persist_install_base_path(base_path, config_file=None):
        """持久化安装根目录并刷新运行时配置"""
        if not base_path:
            PrintUtils.print_error("安装路径不能为空")
            return False

        normalized = os.path.abspath(os.path.expanduser(base_path.strip().strip('"').strip("'")))
        # EXE(onefile) 下：写入 %LOCALAPPDATA%\\fishros_install\\config.py，确保可持久化
        config_path = None
        if config_file:
            config_path = config_file
        else:
            local_appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
            if is_windows and local_appdata:
                cfg_dir = os.path.join(local_appdata, "fishros_install")
                config_path = os.path.join(cfg_dir, "config.py")
                try:
                    os.makedirs(cfg_dir, exist_ok=True)
                except Exception:
                    pass
            if not config_path:
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "config.py"
                )

        # 若目标 config 不存在：尝试从内置/项目模板拷贝一份再写入
        if not os.path.exists(config_path):
            try:
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                root_cfg = os.path.join(project_root, "config.py")
                bundled = None
                if getattr(sys, "frozen", False):
                    meipass = getattr(sys, "_MEIPASS", None)
                    if meipass:
                        candidate = os.path.join(meipass, "config.py")
                        if os.path.exists(candidate):
                            bundled = candidate

                if bundled:
                    shutil.copyfile(bundled, config_path)
                elif os.path.exists(root_cfg):
                    shutil.copyfile(root_cfg, config_path)
                else:
                    # 最小模板兜底
                    FileUtils.write(
                        config_path,
                        "# -*- coding: utf-8 -*-\n"
                        "WINGET_INSTALL_PATH = r'D:\\\\CodeTools'\n"
                        "MSYS2_PATHS = [r'D:\\\\CodeTools\\\\msys64', r'D:\\\\CodeTools', r'C:\\\\msys64', r'C:\\\\msys32']\n"
                        "ARM_GCC_INSTALL_DIR = r'D:\\\\CodeTools\\\\Compiler'\n"
                    )
            except Exception as e:
                PrintUtils.print_error(f"创建配置文件失败: {e}")
                return False

        msys2_path = os.path.join(normalized, "msys64")
        arm_gcc_path = os.path.join(normalized, "Compiler")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            base_raw = ConfigUtils._to_raw_string(normalized)
            msys2_raw = ConfigUtils._to_raw_string(msys2_path)
            arm_raw = ConfigUtils._to_raw_string(arm_gcc_path)

            content = re.sub(
                r"WINGET_INSTALL_PATH\s*=\s*r'[^']*'",
                lambda _: f"WINGET_INSTALL_PATH = r'{base_raw}'",
                content,
                count=1
            )
            content = re.sub(
                r"MSYS2_PATHS\s*=\s*\[[\s\S]*?\]",
                lambda _: (
                    "MSYS2_PATHS = [\n"
                    f"    r'{msys2_raw}',  # 期望的安装路径\n"
                    f"    r'{base_raw}',  # 兼容已安装在此路径的情况\n"
                    "    r'C:\\msys64',\n"
                    "    r'C:\\msys32',\n"
                    "]"
                ),
                content,
                count=1
            )
            content = re.sub(
                r"ARM_GCC_INSTALL_DIR\s*=\s*r'[^']*'",
                lambda _: f"ARM_GCC_INSTALL_DIR = r'{arm_raw}'",
                content,
                count=1
            )

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            PrintUtils.print_error(f"写入配置文件失败: {e}")
            return False

        # 同步当前进程中的配置模块，确保本次运行立即生效
        config_module = sys.modules.get("config")
        if config_module:
            config_module.WINGET_INSTALL_PATH = normalized
            config_module.MSYS2_PATHS = [msys2_path, normalized, r"C:\msys64", r"C:\msys32"]
            config_module.ARM_GCC_INSTALL_DIR = arm_gcc_path

        global WINGET_INSTALL_PATH
        WINGET_INSTALL_PATH = normalized
        WingetUtils.DEFAULT_INSTALL_PATH = normalized
        return True


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
