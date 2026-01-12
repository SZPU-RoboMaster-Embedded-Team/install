# -*- coding: utf-8 -*-
"""
配置文件 - 用于自定义安装工具的行为
"""

# ==================== 安装路径配置 ====================

# Winget 默认安装路径
# 所有通过 winget 安装的软件都会尝试安装到此目录
# 注意: 某些软件包可能不支持自定义安装路径
WINGET_INSTALL_PATH = r'D:\CodeTools'

# MSYS2 安装路径（用于检测和配置）
# 第一个路径是期望的安装路径（用于新安装）
# 其他路径是备选检测路径（用于兼容已安装的情况）
MSYS2_PATHS = [
    r'D:\CodeTools\msys64',  # 期望的安装路径
    r'D:\CodeTools',  # 兼容已安装在此路径的情况
    r'C:\msys64',
    r'C:\msys32',
]

# ARM GCC 工具链安装目录
ARM_GCC_INSTALL_DIR = r'D:\CodeTools\Compiler'

# ==================== 镜像源配置 ====================

# 默认使用的镜像源
# 可选值: 'tsinghua' (清华源), 'ustc' (中科大源), 'official' (官方源)
DEFAULT_MIRROR = 'tsinghua'

# 清华大学镜像源
TSINGHUA_MIRROR = {
    'msys2': 'https://mirrors.tuna.tsinghua.edu.cn/msys2/mingw/x86_64',
}

# 中国科学技术大学镜像源
USTC_MIRROR = {
    'msys2': 'https://mirrors.ustc.edu.cn/msys2/mingw/x86_64',
}

# ==================== 下载配置 ====================

# 下载超时时间（秒）
DOWNLOAD_TIMEOUT = 300

# 是否显示下载进度
SHOW_DOWNLOAD_PROGRESS = True

# ==================== 其他配置 ====================

# 是否自动生成配置文件
AUTO_GENERATE_CONFIG = True

# 配置文件保存路径
# None 表示使用系统临时目录
CONFIG_FILE_PATH = None

# 是否在安装前检查磁盘空间
CHECK_DISK_SPACE = True

# 最小所需磁盘空间（MB）
MIN_DISK_SPACE_MB = 1024
