# -*- coding: utf-8 -*-
"""
Windows 平台一键安装工具
仿照 fishros/install 项目，适配 Windows 平台
使用 winget 作为包管理器
"""
import os
import sys

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
    # 后续可以添加更多工具
    # 4: {'tip':'一键安装: Git for Windows', 'type':INSTALL_DEV, 'tool':'tools/tool_install_git.py', 'dep':[]},
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


def main():
    """主函数"""
    # 检查环境
    if not check_environment():
        return False

    # 导入工具类
    from tools.base import CmdTask, FileUtils, PrintUtils, ChooseTask, ChooseWithCategoriesTask
    from tools.base import osversion, osarch
    from tools.base import run_tool_file
    from tools.base import config_helper

    # 打印欢迎信息
    tip = """
===============================================================================
======  欢迎使用 Windows 一键安装工具，让软件安装更简单！  ======
======  本工具基于 fishros/install 项目，适配 Windows 平台  ======
======  项目地址: https://github.com/fishros/install_make  ======
===============================================================================
    """

    book = """
                    .-~~~~~~~~~-._       _.-~~~~~~~~~-.
                __.'              ~.   .~              `.__
            .'//     开卷有益        \./     书山有路     \\ `.
            .'// 可以多看看小鱼的文章  | 关注B站鱼香ROS机器人 \\ `.
        .'// .-~~~~~~~~~~~~~~-._     |     _,-~~~~~~~~~~~. \\`.
        .'//.-"                 `-.  |  .-'                 "-.\\`.
    .'//______.============-..   \ | /   ..-============.______\\`.
    .'______________________________\|/______________________________`
    ----------------------------------------------------------------------
    """

    end_tip = """
===============================================================================
如果觉得工具好用，请给个 star，如果你想和小鱼一起编写工具，请关注 B站/公众号 <鱼香ROS>
更多工具教程，请访问鱼香ROS官方网站: http://fishros.com
    """

    PrintUtils.print_delay(tip, 0.001)
    PrintUtils.print_delay(book, 0.001)

    # 显示系统信息
    PrintUtils.print_info(f"系统版本: {osversion}")
    PrintUtils.print_info(f"系统架构: {osarch}")
    PrintUtils.print_info(f"Python 版本: {sys.version.split()[0]}")
    print()

    # 选择工具
    code, result = ChooseWithCategoriesTask(
        tool_categories,
        tips="--- 众多工具，等君来用 ---",
        categories=tools_type_map
    ).run()

    if code == 0:
        PrintUtils.print_success("是觉得没有合胃口的菜吗？那快联系小鱼增加菜单吧~")
    else:
        # 运行选中的工具
        run_tool_file(tools[code]['tool'].replace("/", "."))

    # 生成配置文件
    if os.environ.get('GITHUB_ACTIONS') != 'true' and os.environ.get('FISH_INSTALL_CONFIG') is None:
        config_helper.gen_config_file()
        PrintUtils.print_delay("欢迎加入机器人学习交流QQ群：438144612 (入群口令：一键安装)", 0.05)
        PrintUtils.print_delay(
            "鱼香小铺正式开业，最低599可入手一台能建图会导航的移动机器人，淘宝搜店：鱼香ROS",
            0.001
        )
        PrintUtils.print_delay(
            "如在使用过程中遇到问题，请打开：https://fishros.org.cn/forum 进行反馈",
            0.001
        )

    PrintUtils.print_delay(end_tip, 0.001)


if __name__ == '__main__':
    run_exc = []

    try:
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
