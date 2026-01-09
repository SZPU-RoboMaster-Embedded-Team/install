#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARM GCC 工具链环境配置脚本
在安装 MSYS2 和 ARM GCC 后运行此脚本，一次性解决临时目录问题
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}\n")

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}")

def print_info(msg):
    print(f"ℹ {msg}")

def create_global_temp_dir():
    """创建全局临时目录"""
    temp_dir = Path("D:/Temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"创建全局临时目录: {temp_dir}")
    return temp_dir

def configure_msys2_profile():
    """配置 MSYS2 的环境变量"""
    msys2_dir = Path("D:/msys64")

    if not msys2_dir.exists():
        print_error(f"MSYS2 目录不存在: {msys2_dir}")
        print_info("请确认 MSYS2 安装路径，或修改此脚本中的路径")
        return False

    profile_dir = msys2_dir / "etc" / "profile.d"
    profile_dir.mkdir(parents=True, exist_ok=True)

    profile_file = profile_dir / "arm-gcc-temp.sh"

    profile_content = '''# ARM GCC 工具链临时目录配置
# 自动生成 - 解决 ARM GCC 编译时的临时目录权限问题
export TMP="/d/Temp"
export TEMP="/d/Temp"
export TMPDIR="/d/Temp"
'''

    profile_file.write_text(profile_content, encoding='utf-8')
    print_success(f"配置 MSYS2 环境文件: {profile_file}")
    return True

def configure_windows_env():
    """配置 Windows 用户环境变量"""
    try:
        # 使用 setx 命令设置用户环境变量
        subprocess.run(['setx', 'TMP', 'D:\\Temp'],
                      capture_output=True, check=True)
        subprocess.run(['setx', 'TEMP', 'D:\\Temp'],
                      capture_output=True, check=True)
        print_success("配置 Windows 用户环境变量")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"配置 Windows 环境变量失败: {e}")
        return False

def create_cmake_template():
    """创建 CMake 工具链模板"""
    template_dir = Path("D:/E/install_make/cmake_templates")
    template_dir.mkdir(parents=True, exist_ok=True)

    # 创建通用的 CMake 包含文件
    cmake_temp_fix = template_dir / "temp_fix.cmake"
    cmake_content = '''# ARM GCC 临时目录修复
# 在你的 CMakeLists.txt 末尾添加: include(path/to/temp_fix.cmake)

# 设置链接器包装器来控制临时目录
if(TARGET ${CMAKE_PROJECT_NAME})
    set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES
        RULE_LAUNCH_LINK "${CMAKE_COMMAND} -E env TMP=${CMAKE_BINARY_DIR}/tmp TEMP=${CMAKE_BINARY_DIR}/tmp TMPDIR=${CMAKE_BINARY_DIR}/tmp"
    )
endif()
'''
    cmake_temp_fix.write_text(cmake_content, encoding='utf-8')
    print_success(f"创建 CMake 模板: {cmake_temp_fix}")

    # 创建工具链修改说明
    readme = template_dir / "README.md"
    readme_content = '''# ARM GCC 临时目录修复模板

## 使用方法

### 方法1: 在 CMakeLists.txt 中包含修复文件

在你的 `CMakeLists.txt` 文件末尾添加:

```cmake
# 包含临时目录修复
include(D:/E/install_make/cmake_templates/temp_fix.cmake)
```

### 方法2: 在 gcc-arm-none-eabi.cmake 中添加 -pipe 标志

在 `CMAKE_C_FLAGS` 和 `CMAKE_CXX_FLAGS` 设置后添加:

```cmake
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -pipe")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pipe")
```

### 方法3: 使用批量处理脚本

```bash
python D:/E/install_make/apply_temp_fix.py <你的项目目录>
```

## 验证环境配置

重启终端后运行:

```bash
echo $TMP
# 应该显示: /d/Temp
```

## 新项目模板

创建新项目时，确保:

1. 环境变量已正确设置（重启终端后自动生效）
2. CMakeLists.txt 包含临时目录修复
3. 或者在工具链文件中添加 -pipe 标志
'''
    readme.write_text(readme_content, encoding='utf-8')
    print_success(f"创建使用说明: {readme}")

    return template_dir

def main():
    print_header("ARM GCC 工具链环境配置")

    print_info("此脚本将配置全局环境，解决 ARM GCC 编译时的临时目录问题")
    print_info("配置后，所有新项目都将自动使用正确的临时目录\n")

    # 1. 创建全局临时目录
    create_global_temp_dir()

    # 2. 配置 MSYS2
    if not configure_msys2_profile():
        print_error("MSYS2 配置失败，请检查安装路径")
        return 1

    # 3. 配置 Windows 环境变量
    configure_windows_env()

    # 4. 创建 CMake 模板
    template_dir = create_cmake_template()

    print_header("配置完成")

    print("✓ 全局环境已配置")
    print("✓ MSYS2 环境已配置")
    print("✓ Windows 环境变量已设置")
    print(f"✓ CMake 模板已创建: {template_dir}")

    print("\n" + "="*60)
    print("重要提示:")
    print("="*60)
    print("1. 请关闭并重新打开所有终端窗口")
    print("2. 重新打开后，环境变量将自动生效")
    print("3. 对于现有项目，运行以下命令应用修复:")
    print(f"   python {Path(__file__).parent}/apply_temp_fix.py <项目目录>")
    print("4. 对于新项目，环境变量会自动生效，无需额外配置")
    print("\n验证方法:")
    print("  在新终端中运行: echo $TMP")
    print("  应该显示: /d/Temp")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
