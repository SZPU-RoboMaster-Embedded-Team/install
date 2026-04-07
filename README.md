# Windows 一键安装工具 (install_make)

> ### 仿照 [fishros/install](https://github.com/fishros/install) 项目，适配 Windows 平台的一键安装工具

## 项目简介

这是一个专为 Windows 平台设计的一键安装工具，灵感来源于小鱼的 [fishros/install](https://github.com/fishros/install) 项目。本工具使用 Python 编写，通过 winget 包管理器实现软件的快速安装和配置。

## 系统要求

- Windows 10/11 (推荐)
- Python 3.6 或更高版本
- winget (Windows 应用安装程序，Windows 10/11 自带)

## 使用方法

### 方法一：使用批处理脚本（推荐）

1. 右键,以管理员身份运行 `run.bat`
2. 按照提示选择要安装的工具

### 方法二：使用 Python 直接运行

```bash
python install.py
```

### 方法三：直接运行exe

- 右键,以管理员身份运行install.exe

## 项目结构

```
install_make/
├── install.py              # 主入口文件
├── run.bat                 # Windows 批处理启动脚本
├── config.py               # 配置文件（可自定义安装路径等）
├── README.md               # 项目说明文档
├── QUICKSTART.md           # 快速开始指南
└── tools/                  # 工具模块目录
    ├── __init__.py         # Python 包标识文件
    ├── base.py             # 基础工具类（适配 Windows）
    └── tool_install_msys2.py  # MSYS2 安装工具
└── example/                # 工具测试

```

## 自定义安装路径

默认情况下，所有通过 winget 安装的软件会尝试安装到 `D:\CodeTools` 目录。

程序启动后会先提示你选择安装目录模式：
- `1. 默认路径`
- `2. 自定义路径（支持直接粘贴）`

选择自定义路径后，工具会自动创建目录（若不存在），并将路径写回 `config.py`，下次启动会继续使用该路径。

### 快速修改

编辑 [config.py](d:\E\install_make\config.py) 文件，修改 `WINGET_INSTALL_PATH` 变量：

```python
# 修改为你想要的安装路径
WINGET_INSTALL_PATH = r'D:\CodeTools'  # 可以改为 E:\MyApps 等
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

## 配置文件自动化

工具支持通过配置文件实现自动化安装，配置文件会在运行后自动生成在 `%TEMP%\fish_install.yaml`。

## 与 Linux 版本的对应关系

| Linux 版本 | Windows 版本 | 说明     |
| ---------- | ------------ | -------- |
| apt        | winget       | 包管理器 |
| wget/curl  | urllib       | 下载工具 |
| bash       | Python       | 脚本语言 |
| /tmp/      | %TEMP%       | 临时目录 |
| sudo       | 管理员权限   | 权限提升 |

## 常见问题

### 1. 提示 "winget 不可用"

**解决方法**：
- 确保你使用的是 Windows 10 (1809+) 或 Windows 11
- 在 Microsoft Store 中搜索并安装 "应用安装程序"
- 或访问 [winget 官方页面](https://github.com/microsoft/winget-cli) 下载安装

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

## 开源协议

本项目遵循与原项目相同的开源协议。

---

**如果觉得工具好用，请给个 Star ⭐**


