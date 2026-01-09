#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为现有项目添加临时目录修复的脚本
自动修改项目的 CMakeLists.txt 和 gcc-arm-none-eabi.cmake
"""

import os
import sys
import re
from pathlib import Path

def add_temp_fix_to_cmake(cmake_file):
    """在 CMakeLists.txt 中添加临时目录修复"""
    if not cmake_file.exists():
        print(f"错误: 找不到文件 {cmake_file}")
        return False

    content = cmake_file.read_text(encoding='utf-8')

    # 检查是否已经添加过
    if 'RULE_LAUNCH_LINK' in content:
        print(f"✓ {cmake_file.name} 已经包含临时目录修复")
        return True

    # 在文件末尾添加修复代码
    fix_code = '''
# 设置链接器包装器来控制临时目录（修复 C:\\Windows\\ 权限问题）
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
    RULE_LAUNCH_LINK "${CMAKE_COMMAND} -E env TMP=${CMAKE_BINARY_DIR}/tmp TEMP=${CMAKE_BINARY_DIR}/tmp TMPDIR=${CMAKE_BINARY_DIR}/tmp"
)
'''

    # 在最后一个 ) 之后添加
    content = content.rstrip() + '\n' + fix_code

    cmake_file.write_text(content, encoding='utf-8')
    print(f"✓ 已修改 {cmake_file.name}")
    return True

def add_pipe_flag_to_toolchain(toolchain_file):
    """在 gcc-arm-none-eabi.cmake 中添加 -pipe 标志"""
    if not toolchain_file.exists():
        print(f"错误: 找不到文件 {toolchain_file}")
        return False

    content = toolchain_file.read_text(encoding='utf-8')

    # 检查是否已经添加过
    if '-pipe' in content:
        print(f"✓ {toolchain_file.name} 已经包含 -pipe 标志")
        return True

    # 在 CMAKE_C_FLAGS 后添加 -pipe
    content = re.sub(
        r'(set\(CMAKE_C_FLAGS "\$\{CMAKE_C_FLAGS\} \$\{TARGET_FLAGS\}"\))',
        r'\1\nset(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pipe")  # 使用管道而不是临时文件',
        content
    )

    # 在 CMAKE_CXX_FLAGS 后添加 -pipe
    content = re.sub(
        r'(set\(CMAKE_CXX_FLAGS "\$\{CMAKE_C_FLAGS\}[^"]*"\))',
        r'\1\nset(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pipe")  # 使用管道而不是临时文件',
        content
    )

    toolchain_file.write_text(content, encoding='utf-8')
    print(f"✓ 已修改 {toolchain_file.name}")
    return True

def process_project(project_dir):
    """处理单个项目"""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"错误: 项目目录不存在: {project_dir}")
        return False

    print(f"\n处理项目: {project_path.name}")
    print("=" * 60)

    # 查找 CMakeLists.txt
    cmake_file = project_path / "CMakeLists.txt"
    if cmake_file.exists():
        add_temp_fix_to_cmake(cmake_file)
    else:
        print(f"警告: 未找到 CMakeLists.txt")

    # 查找 gcc-arm-none-eabi.cmake
    toolchain_file = project_path / "cmake" / "gcc-arm-none-eabi.cmake"
    if toolchain_file.exists():
        add_pipe_flag_to_toolchain(toolchain_file)
    else:
        print(f"警告: 未找到 cmake/gcc-arm-none-eabi.cmake")

    return True

def main():
    print("=" * 60)
    print("ARM GCC 临时目录修复 - 项目批量处理工具")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\n用法:")
        print("  python apply_temp_fix.py <项目目录1> [项目目录2] ...")
        print("\n示例:")
        print("  python apply_temp_fix.py D:/Projects/MyProject")
        print("  python apply_temp_fix.py ../Robot/example/MotorPid")
        return 1

    success_count = 0
    for project_dir in sys.argv[1:]:
        if process_project(project_dir):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"处理完成: {success_count}/{len(sys.argv)-1} 个项目成功")
    print("=" * 60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
