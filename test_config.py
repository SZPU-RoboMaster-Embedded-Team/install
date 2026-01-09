# -*- coding: utf-8 -*-
"""
测试配置加载
"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from tools.base import PrintUtils, WingetUtils

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("配置测试")
    print("=" * 60)
    print()

    PrintUtils.print_info(f"当前 winget 默认安装路径: {WingetUtils.DEFAULT_INSTALL_PATH}")
    print()

    # 检查路径是否存在
    import os
    if os.path.exists(WingetUtils.DEFAULT_INSTALL_PATH):
        PrintUtils.print_success(f"✓ 安装目录已存在: {WingetUtils.DEFAULT_INSTALL_PATH}")
    else:
        PrintUtils.print_warning(f"⚠ 安装目录不存在，将在首次安装时自动创建")
        PrintUtils.print_info(f"  目标路径: {WingetUtils.DEFAULT_INSTALL_PATH}")

    print()
    PrintUtils.print_info("如需修改安装路径，请编辑 config.py 文件")
    PrintUtils.print_info("修改 WINGET_INSTALL_PATH 变量为你想要的路径")
    print()

    PrintUtils.print_success("=" * 60)
    PrintUtils.print_success("配置测试完成!")
    PrintUtils.print_success("=" * 60)

if __name__ == '__main__':
    try:
        test_config()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
