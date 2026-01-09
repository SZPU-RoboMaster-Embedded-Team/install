# Windows 一键安装工具 (install_make)

> ### 仿照 [fishros/install](https://github.com/fishros/install) 项目，适配 Windows 平台的一键安装工具

## 项目简介

这是一个专为 Windows 平台设计的一键安装工具，灵感来源于小鱼的 [fishros/install](https://github.com/fishros/install) 项目。本工具使用 Python 编写，通过 winget 包管理器实现软件的快速安装和配置。

## 特性

- ✅ 使用 **winget** 作为包管理器（Windows 官方支持）
- ✅ 使用 **Python** 编写，跨平台兼容性好
- ✅ 使用 **Python 内置库**处理下载，无需额外依赖
- ✅ 交互式菜单，操作简单
- ✅ 支持配置文件自动化安装
- ✅ 模块化设计，易于扩展

## 已支持工具列表

- ✅ 一键安装: MSYS2 (Windows 上的类 Unix 环境)
  - 支持 winget 自动安装
  - 支持手动下载安装
  - 支持配置国内镜像源（清华源、中科大源）
  - 支持自动更新系统

## 系统要求

- Windows 10/11 (推荐)
- Python 3.6 或更高版本
- winget (Windows 应用安装程序，Windows 10/11 自带)

## 使用方法

### 方法一：使用批处理脚本（推荐）

1. 双击运行 `run.bat`
2. 按照提示选择要安装的工具

### 方法二：使用 Python 直接运行

```bash
python install.py
```

### 方法三：在线一键安装（开发中）

```powershell
# 计划支持类似 Linux 版本的在线安装方式
# powershell -c "irm http://fishros.com/install_win | iex"
```

## 项目结构

```
install_make/
├── install.py              # 主入口文件
├── run.bat                 # Windows 批处理启动脚本
├── config.py               # 配置文件（可自定义安装路径等）
├── test_basic.py           # 基础功能测试脚本
├── README.md               # 项目说明文档
├── QUICKSTART.md           # 快速开始指南
└── tools/                  # 工具模块目录
    ├── __init__.py         # Python 包标识文件
    ├── base.py             # 基础工具类（适配 Windows）
    └── tool_install_msys2.py  # MSYS2 安装工具
```

## 自定义安装路径

默认情况下，所有通过 winget 安装的软件会尝试安装到 `D:\wingetApp` 目录。

### 快速修改

编辑 [config.py](d:\E\install_make\config.py) 文件，修改 `WINGET_INSTALL_PATH` 变量：

```python
# 修改为你想要的安装路径
WINGET_INSTALL_PATH = r'D:\wingetApp'  # 可以改为 E:\MyApps 等
```

### 详细说明

查看 [安装路径自定义指南](INSTALL_PATH_GUIDE.md) 了解：
- 如何修改默认安装路径
- winget 的 --location 参数限制
- 常见问题和解决方案
- 验证配置的方法

### 注意事项

- ⚠️ 某些软件包可能不支持自定义安装路径（winget 限制）
- ✅ 确保目标磁盘有足够的空间
- ✅ 路径会自动创建，无需手动创建目录
- ✅ 运行 `python test_config.py` 验证配置

## 工具类说明

### base.py 提供的工具类

- **PrintUtils**: 打印工具类，支持彩色输出
- **CmdTask**: 命令执行任务类
- **FileUtils**: 文件操作工具类，支持下载
- **WingetUtils**: Winget 包管理工具类
- **ChooseTask**: 选择任务类
- **ChooseWithCategoriesTask**: 带分类的选择任务类
- **BaseTool**: 工具基类
- **ConfigHelper**: 配置文件助手

### 编写自己的安装工具

1. 在 `tools/` 目录下创建新文件，命名格式：
   - 安装工具: `tool_install_xxx.py`
   - 配置工具: `tool_config_xxx.py`

2. 使用以下模板：

```python
# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, WingetUtils, ChooseTask
from .base import osversion, osarch

class Tool(BaseTool):
    def __init__(self):
        self.name = "工具名称"
        self.type = BaseTool.TYPE_INSTALL  # 或 BaseTool.TYPE_CONFIG
        self.author = '你的名字'

    def run(self):
        # 在这里编写安装逻辑
        PrintUtils.print_info("开始安装...")

        # 使用 winget 安装
        WingetUtils.install("PackageID")

        PrintUtils.print_success("安装完成!")
```

3. 在 `install.py` 的 `tools` 字典中添加工具信息：

```python
tools = {
    1: {'tip':'一键安装: MSYS2', 'type':INSTALL_SOFTWARE, 'tool':'tools/tool_install_msys2.py', 'dep':[]},
    2: {'tip':'你的工具描述', 'type':INSTALL_SOFTWARE, 'tool':'tools/tool_install_xxx.py', 'dep':[]},
}
```

## 配置文件自动化

工具支持通过配置文件实现自动化安装，配置文件会在运行后自动生成在 `%TEMP%\fish_install.yaml`。

### 使用配置文件

1. 手动运行一次工具，完成后会生成配置文件
2. 将配置文件复制到当前目录或设置环境变量 `FISH_INSTALL_CONFIG`
3. 再次运行时会自动使用配置文件中的选项

### 配置文件示例

```yaml
chooses:
- {choose: 1, desc: '一键安装: MSYS2'}
- {choose: 1, desc: '使用 winget 安装（推荐）'}
- {choose: 1, desc: '配置国内镜像源（清华源）'}
time: '1704844800.0'
```

## 与 Linux 版本的对应关系

| Linux 版本 | Windows 版本 | 说明 |
|-----------|-------------|------|
| apt | winget | 包管理器 |
| wget/curl | urllib | 下载工具 |
| bash | Python | 脚本语言 |
| /tmp/ | %TEMP% | 临时目录 |
| sudo | 管理员权限 | 权限提升 |

## 常见问题

### 1. 提示 "winget 不可用"

**解决方法**：
- 确保你使用的是 Windows 10 (1809+) 或 Windows 11
- 在 Microsoft Store 中搜索并安装 "应用安装程序"
- 或访问 [winget 官方页面](https://github.com/microsoft/winget-cli) 下载安装

### 2. Python 未安装

**解决方法**：
```bash
# 使用 winget 安装 Python
winget install Python.Python.3

# 或访问官网下载
# https://www.python.org/downloads/
```

### 3. 权限不足

某些操作可能需要管理员权限，请右键选择 "以管理员身份运行" `run.bat`。

## 计划支持的工具

- [ ] Git for Windows
- [ ] VSCode
- [ ] Python
- [ ] Node.js
- [ ] Docker Desktop
- [ ] CMake
- [ ] MinGW
- [ ] 更多开发工具...

## 贡献指南

欢迎贡献新的安装工具！请参考上面的"编写自己的安装工具"部分。

1. Fork 本项目
2. 创建新的工具文件
3. 在 `install.py` 中注册工具
4. 测试确保功能正常
5. 提交 Pull Request

## 致谢

- 感谢 [小鱼](https://github.com/fishros) 的 [fishros/install](https://github.com/fishros/install) 项目提供灵感
- 感谢所有贡献者

## 相关链接

- 原项目（Linux 版本）: https://github.com/fishros/install
- 鱼香ROS官网: http://fishros.com
- B站: 鱼香ROS机器人
- QQ群: 438144612 (入群口令：一键安装)

## 开源协议

本项目遵循与原项目相同的开源协议。

---

**如果觉得工具好用，请给个 Star ⭐**
