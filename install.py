# -*- coding: utf-8 -*-
"""
Windows 平台一键安装工具
仿照 fishros/install 项目，适配 Windows 平台
使用 winget 作为包管理器
"""
import os
import sys
import ctypes
import subprocess


def _ensure_persistent_config_on_windows():
    """EXE(onefile) 场景：确保使用可持久化的 config.py（不写入 _MEI 临时目录）。

    - 优先路径: %LOCALAPPDATA%\\fishros_install\\config.py
    - 若不存在且当前为 frozen，则尝试从 sys._MEIPASS\\config.py 拷贝
    """
    if os.name != "nt":
        return

    try:
        local_appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if not local_appdata:
            return

        cfg_dir = os.path.join(local_appdata, "fishros_install")
        cfg_path = os.path.join(cfg_dir, "config.py")
        os.makedirs(cfg_dir, exist_ok=True)

        # 若 config.py 不存在且为 EXE 模式，尝试从打包内置模板拷贝一份
        if not os.path.exists(cfg_path) and getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                bundled = os.path.join(meipass, "config.py")
                if os.path.exists(bundled):
                    import shutil
                    shutil.copyfile(bundled, cfg_path)

        # 让 import config 优先从持久化目录加载
        if os.path.exists(cfg_path):
            if cfg_dir not in sys.path:
                sys.path.insert(0, cfg_dir)
    except Exception:
        # 任何异常不影响主流程
        return

# 工具类型定义
INSTALL_SOFTWARE = 0  # 安装软件
CONFIG_TOOL = 1  # 配置相关
INSTALL_DEV = 2  # 开发工具

tools_type_map = {
    INSTALL_SOFTWARE: "常用软件",
    CONFIG_TOOL: "配置工具",
    INSTALL_DEV: "开发工具"
}

# 工具列表
tools = {
    1: {
        'tip': '一键安装: MSYS2 (Windows 上的类 Unix 环境)',
        'type': INSTALL_SOFTWARE,
        'tool': 'tools/tool_install_msys2.py',
        'dep': []
    },
    2: {
        'tip': '一键安装: GCC、Make 和 CMake (通过 MSYS2)',
        'type': INSTALL_DEV,
        'tool': 'tools/tool_install_make_cmake.py',
        'dep': []
    },
    3: {
        'tip': '一键安装: OpenOCD (通过 MSYS2)',
        'type': INSTALL_DEV,
        'tool': 'tools/tool_install_openocd.py',
        'dep': []
    },
    4: {
        'tip': '一键安装: ARM GCC 工具链 (arm-none-eabi-gcc)',
        'type': INSTALL_DEV,
        'tool': 'tools/tool_install_armgcc.py',
        'dep': []
    },
    # 后续可以添加更多工具
    # 5: {'tip':'一键安装: Git for Windows', 'type':INSTALL_DEV, 'tool':'tools/tool_install_git.py', 'dep':[]},
    # 5: {'tip':'一键安装: VSCode', 'type':INSTALL_DEV, 'tool':'tools/tool_install_vscode.py', 'dep':[]},
    # 6: {'tip':'一键安装: Python', 'type':INSTALL_DEV, 'tool':'tools/tool_install_python.py', 'dep':[]},
}

# 创建用于存储不同类型工具的字典
tool_categories = {}

# 遍历 tools 字典，根据 type 值进行分类
for tool_id, tool_info in tools.items():
    tool_type = tool_info['type']
    if tool_type not in tool_categories:
        tool_categories[tool_type] = {}
    tool_categories[tool_type][tool_id] = tool_info


def check_environment():
    """检查运行环境"""
    import platform

    if platform.system() != 'Windows':
        print("错误: 此工具仅支持 Windows 平台")
        print("如果你在使用 Linux，请访问: https://github.com/fishros/install")
        return False

    # 检查 Python 版本
    if sys.version_info < (3, 6):
        print("错误: 需要 Python 3.6 或更高版本")
        print(f"当前版本: Python {sys.version}")
        return False

    return True


def is_admin():
    """检查当前进程是否具备管理员权限。"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    """在 Windows 下以管理员权限重启当前脚本/程序。"""
    if getattr(sys, "frozen", False):
        executable = sys.executable
        params = subprocess.list2cmdline(sys.argv[1:])
    else:
        executable = sys.executable
        script_path = os.path.abspath(__file__)
        params = subprocess.list2cmdline([script_path] + sys.argv[1:])

    rc = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        params,
        None,
        1,
    )
    return rc > 32


def ensure_admin_on_windows():
    """如果不是管理员，则触发 UAC 提权并退出当前进程。"""
    if os.name != "nt":
        return True

    if is_admin():
        return True

    print("检测到当前不是管理员权限，正在请求提权...")
    if relaunch_as_admin():
        return False

    print("管理员权限请求失败，或已取消 UAC。")
    return False


def main():
    """主函数"""
    # 检查环境
    if not check_environment():
        return False

    _ensure_persistent_config_on_windows()

    # 导入工具类
    from tools.base import CmdTask, FileUtils, PrintUtils, ChooseTask, ChooseWithCategoriesTask, ConfigUtils
    from tools.base import osversion, osarch
    from tools.base import run_tool_file

    # 打印欢迎信息
    tip = """
===============================================================================
======  欢迎使用 Windows 一键安装工具，让软件安装更简单！  ======
======  本工具基于 fishros/install 项目，适配 Windows 平台  ======
===============================================================================
    """

#     book = """
#                     .-~~~~~~~~~-._       _.-~~~~~~~~~-.
#                 __.'              ~.   .~              `.__
#             .'//     开卷有益        \./     书山有路     \\ `.
#             .'// 可以多看看小鱼的文章  | 关注B站鱼香ROS机器人 \\ `.
#         .'// .-~~~~~~~~~~~~~~-._     |     _,-~~~~~~~~~~~. \\`.
#         .'//.-"                 `-.  |  .-'                 "-.\\`.
#     .'//______.============-..   \ | /   ..-============.______\\`.
#     .'______________________________\|/______________________________`
#     ----------------------------------------------------------------------
#     """

#     end_tip = """
# ===============================================================================
# 如果觉得工具好用，请给个 star，如果你想和小鱼一起编写工具，请关注 B站/公众号 <鱼香ROS>
# 更多工具教程，请访问鱼香ROS官方网站: http://fishros.com
#     """

    end_tip = ""

    PrintUtils.print_delay(tip, 0.001)
    # PrintUtils.print_delay(book, 0.001)

    # 显示系统信息
    PrintUtils.print_info(f"系统版本: {osversion}")
    PrintUtils.print_info(f"系统架构: {osarch}")
    PrintUtils.print_info(f"Python 版本: {sys.version.split()[0]}")
    print()

    # 启动时让用户选择安装目录（默认/自定义）
    try:
        import config
        current_base_path = getattr(config, "WINGET_INSTALL_PATH", r"D:\CodeTools")
    except Exception:
        current_base_path = r"D:\CodeTools"

    # 如果默认安装目录不存在，自动回退到 D:\CodeTools（按用户期望，不自动创建错误目录）
    fallback_base_path = r"D:\CodeTools"
    try:
        if not current_base_path or not os.path.isdir(current_base_path):
            current_base_path = fallback_base_path
    except Exception:
        current_base_path = fallback_base_path

    PrintUtils.print_info(f"当前默认安装目录: {current_base_path}")
    path_options = {
        1: "使用默认路径",
        2: "使用自定义路径（支持粘贴）",
    }
    path_code, _ = ChooseTask(path_options, "请选择安装目录模式:").run()
    if path_code == 0:
        PrintUtils.print_info("用户取消，程序退出")
        return False

    selected_base_path = current_base_path
    if path_code == 2:
        while True:
            pasted_path = input("\n请粘贴安装根目录路径: ").strip().strip('"').strip("'")
            if not pasted_path:
                PrintUtils.print_warning("路径不能为空，请重新输入")
                continue

            selected_base_path = os.path.abspath(os.path.expanduser(pasted_path))
            try:
                os.makedirs(selected_base_path, exist_ok=True)
                PrintUtils.print_info(f"已确认安装目录: {selected_base_path}")
                break
            except Exception as e:
                PrintUtils.print_error(f"无法创建目录: {e}")
    else:
        # 默认模式也确保回退目录存在（只创建 D:\CodeTools，不创建用户配置里的错误路径）
        try:
            if selected_base_path == fallback_base_path:
                os.makedirs(selected_base_path, exist_ok=True)
        except Exception as e:
            PrintUtils.print_warning(f"无法创建默认安装目录 {selected_base_path}: {e}")

    # 持久化到配置文件，并刷新本次运行的路径设置
    if not ConfigUtils.persist_install_base_path(selected_base_path):
        PrintUtils.print_warning("安装目录写入配置失败，将继续使用当前运行时配置")

    # 循环选择工具：运行完成后返回主菜单，直到用户选择 0 退出
    while True:
        code, result = ChooseWithCategoriesTask(
            tool_categories,
            tips="--- 众多工具，等君来用 ---",
            categories=tools_type_map
        ).run()

        if code == 0:
            PrintUtils.print_success("是觉得没有合胃口的菜吗？提交issue增加菜单吧~")
            break

        # 运行选中的工具（工具失败不影响继续回到主菜单）
        ok = run_tool_file(tools[code]['tool'].replace("/", "."))
        if not ok:
            PrintUtils.print_warning("工具运行失败，但程序将继续运行，你可以返回菜单选择其他工具。")

    if os.environ.get('GITHUB_ACTIONS') != 'true':
        PrintUtils.print_delay("", 0.05)
        PrintUtils.print_delay(
            "",
            0.001
        )
        PrintUtils.print_delay(
            "如在使用过程中遇到问题，请提交issue进行反馈",
            0.001
        )

    PrintUtils.print_delay(end_tip, 0.001)


if __name__ == '__main__':
    run_exc = []

    try:
        if not ensure_admin_on_windows():
            sys.exit(0)
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        import traceback
        print('\r\n检测到程序发生异常退出，请打开：https://fishros.org.cn/forum 携带如下内容进行反馈\n\n')
        print("标题：使用 Windows 一键安装过程中遇到程序崩溃")
        print("```")
        traceback.print_exc()
        run_exc.append(traceback.format_exc())
        print("```")

        # 保存日志
        try:
            log_path = os.path.join(os.environ.get('TEMP', '.'), 'fishros_install.log')
            with open(log_path, "w", encoding="utf-8") as f:
                for exc in run_exc:
                    print(exc, file=f)
            print(f'本次运行详细日志文件已保存至 {log_path}')
        except:
            pass
