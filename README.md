# AUPT

AUPT--一个统一的 Linux 包管理调度工具(开发中)

# **AUPT (Advanced Unified Package Tool)**
---
## 目录

- [1. 核心功能目标](#1-核心功能目标feature-goals)
  - [1.1 基础功能](#11-基础功能)
  - [1.2 指定包管理器](#12-指定包管理器)
  - [1.3 自动包管理器选择策略](#13-自动包管理器选择策略)
  - [1.4 版本控制支持](#14-版本控制支持)
  - [1.5 镜像源自动优化](#15-镜像源自动优化)
  - [1.6 包搜索与信息查询](#16-包搜索与信息查询)
  - [1.7 系统诊断功能](#37-系统诊断功能)
- [2. 系统总体架构](#2-系统总体架构system-architecture)
- [3. CLI 设计规范](#3-cli-设计规范command-interface)
- [安装](#安装)
  - [方式一：使用安装脚本](#方式一使用安装脚本)
  - [方式二：直接使用 pip](#方式二直接使用-pip)
  - [系统级安装](#系统级安装)
- [console_script 说明](#consolescript-说明)
- [APT 后端说明](#apt-后端说明)
- [PATH 说明](#path-说明)
- [卸载](#卸载)
- [受限环境使用](#受限环境使用)

---

核心目标：

```text
统一命令入口 + 自动识别发行版 + 自动选择包管理器
```
联系开发者：
[邮箱](19589917063@163.com)
[QQ](3299459360)
[X](SCuNF@lcfv171289)
[WhatApp](+8619589917063)
---

## 1. 核心功能目标（Feature Goals）

### 1.1 基础功能

- 自动识别 Linux 发行版
- 自动调用系统对应包管理器
- 支持指定包管理器
- 支持版本控制
- 支持镜像源自动优化
- 支持包搜索与信息查询
- 支持统一安装命令
- 支持统一卸载命令
- 支持统一更新命令

### 支持的操作系统：
- Debian/Ubuntu -- 已适配
- Arch Linux --理论已支持，未测试
- Fedora  --理论已支持，未测试
- OpenSUSE  --理论已支持，未测试
- SUSE Linux Enterprise Server  --理论已支持，未测试
示例：

```bash
aupt install vim
aupt remove gcc
aupt update
aupt upgrade
```

---

### 1.2 指定包管理器

支持用户强制指定工具：

```bash
aupt apt install nginx
aupt pacman install git
aupt snap install code
```

---

### 1.3 自动包管理器选择策略

默认优先级：

```text
apt/pacman/dnf/zypper → flatpak → snap
```

流程：

```text
查询 apt/pacman/dnf/zypper
若不存在 → 查询 flatpak
若不存在 → 查询 snap
```

---

### 1.4 版本控制支持

示例：

```bash
aupt install gcc==9
aupt install python@3.10
```

支持：

- 指定版本安装
- 自动解析版本
- 自动 fallback

---

### 1.5 镜像源自动优化  

支持：

```bash
aupt mirror auto
aupt mirror list
aupt mirror switch tuna
```

功能包括：

- 自动测速镜像源
- 自动选择最快镜像
- 自动修改配置
- 自动更新索引

---

### 1.6 包搜索与信息查询

```bash
aupt search redis
aupt info nodejs
```

---

### 1.7 系统诊断功能

```bash
aupt doctor
```

用于检测：

- 包管理器状态
- 网络状态
- 镜像源状态

---

## 2. 系统总体架构（System Architecture）   

采用：

```text
分层架构 + 插件架构
```

目录结构：

```text
aupt
├── core/
│   ├── dispatcher.py
│   ├── distro_detector.py
│   ├── package_resolver.py
│   ├── mirror_manager.py
│   └── config_manager.py
│
├── backends/
│   ├── base_backend.py
│   ├── apt_backend.py
│   ├── pacman_backend.py
│   ├── dnf_backend.py
│   ├── snap_backend.py
│   ├── flatpak_backend.py
│   └── zypper_backend.py
│
├── cli/
│   ├── parser.py
│   └── commands.py
│
├── utils/
│   ├── mirror_speed_test.py
│   ├── version_parser.py
│   ├── subprocess_wrapper.py
│   └── logger.py
│
├── database/
│   ├── package_alias.json
│   ├── mirror_list.json
│   └── distro_map.json
│
├── plugins/
│
└── main.py

## 说明文档
aupt/
├── README.md                      # 主文档（已更新）
├── QUICK_START.md                 # 快速开始（新增）
├── COMPATIBILITY.md               # 兼容性详细说明（新增）
├── COMPATIBILITY_SUMMARY.md       # 兼容性总结（新增）
├── PYTHON_COMPAT_REPORT.md        # 改进报告（新增）
├── CHANGELOG.md                   # 更新日志（已更新）
├── QUICK_REFERENCE.md             # 快速参考
├── RESTRICTED_ENV.md              # 受限环境指南
├── BUGFIX.md                      # Bug 修复说明
└── scripts/
    ├── install.sh                 # 标准安装（已增强）
    ├── install_compat.sh          # 兼容性安装（新增）
    ├── test_compatibility.sh      # 兼容性测试（新增）
    ├── uninstall.sh               # 卸载脚本
    └── manual_mirror_switch.sh    # 手动镜像切换

```

---

## 3. CLI 设计规范（Command Interface）

标准命令格式：

```text
aupt <manager?> <action> <package> [options]
```

支持命令：

```bash
aupt install vim
aupt remove gcc
aupt update
aupt upgrade

aupt search nginx
aupt info python

aupt mirror auto
aupt mirror list
aupt mirror switch tuna

aupt doctor
aupt clean
aupt config
aupt benchmark
```


## 系统要求

- **Python**: 3.6+ (支持 Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11+)
- **系统**: Linux (Ubuntu 18.04+, Debian 9+, CentOS 7+, Fedora, Arch Linux 等)
- **权限**: 部分功能需要 root 权限（如安装包、切换镜像）

详细的版本兼容性说明请查看 [COMPATIBILITY.md](COMPATIBILITY.md)。

## 安装

### 方式一：使用安装脚本（推荐）

默认执行用户级安装，使用系统 `python3`，**支持 Python 3.6+**：

```bash
# 获取仓库
git clone git@github.com:wusi321/aupt.git
# 将获取的文件夹aupt-main重命名为aupt
cd ~/aupt
chmod +x scripts/install.sh scripts/uninstall.sh
./scripts/install.sh
```

安装脚本会自动：
- 检测 Python 版本（需要 3.6+）
- 处理 `--break-system-packages` 问题
- 配置 PATH 环境变量

安装完成后，命令会通过 `console_script` 暴露为全局可执行命令：

```bash
aupt doctor
aupt install vim --dry-run
```

### 方式二：使用兼容性安装脚本（增强版）

提供更多诊断信息和自动修复功能，**特别适合低版本系统**（如 Ubuntu 18.04）：

```bash
cd ~/aupt
chmod +x scripts/install_compat.sh
./scripts/install_compat.sh
```

**特点**:
- 自动查找可用的 Python 解释器（python3.6, python3.7, python3.8 等）
- 自动安装 pip（如果缺失）
- 彩色输出和详细的诊断信息
- 自动处理各种安装问题

### 方式三：直接使用 `pip`

仍然使用系统 `python3`：

```bash
# 获取仓库
git clone git@github.com:wusi321/aupt.git
# 将获取的文件夹aupt-main重命名为aupt
cd ~/aupt
python3 -m pip install --user .
```

### 指定 Python 版本

如果系统有多个 Python 版本，可以指定使用哪个：

```bash
# 使用 Python 3.8
PYTHON_BIN=python3.8 ./scripts/install.sh

# 使用 Python 3.6
PYTHON_BIN=python3.6 ./scripts/install.sh
```

### 低版本系统安装

**Ubuntu 18.04 (Python 3.6)**:
```bash
sudo apt install python3-pip
./scripts/install.sh
```

**Ubuntu 16.04 (需要升级 Python)**:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.6 python3.6-pip
PYTHON_BIN=python3.6 ./scripts/install.sh
```

更多低版本系统安装指南请查看 [COMPATIBILITY.md](COMPATIBILITY.md)。

### 如果安装失败请尝试
```bash
cd ~/aupt
pip install . --break-system-packages
```

安装完成后可直接执行：

```bash
aupt doctor
```

### 系统级安装

如果你希望所有用户都可直接执行 `aupt`，可以使用系统级安装：

```bash
cd ~/aupt
sudo INSTALL_SCOPE=system ./scripts/install.sh
```

或：

```bash
cd ~/aupt
sudo python3 -m pip install .
```

## `console_script` 说明

项目在 [pyproject.toml](file:///~/aupt/pyproject.toml) 中声明了：   

```toml
[project.scripts]
aupt = "aupt.cli.commands:main"
```

这表示安装完成后，Python 打包系统会自动生成一个名为 `aupt` 的启动命令，实际调用入口函数 `aupt.cli.commands:main`。

因此你不需要手动创建软链接，也不需要自己写启动包装器，只要项目安装成功，就可以直接在终端里执行：

```bash
aupt doctor
aupt config
aupt mirror list
```

## APT 后端说明

在 Debian / Ubuntu 系系统上，AUPT 的 `apt` 后端默认采用更稳定的脚本接口：

```bash
apt-get
apt-cache
```

其中：

```text
安装/卸载/更新/升级/清理 -> apt-get
搜索/信息查询 -> apt-cache
```

这样可以避免直接使用 `apt` 命令时常见的脚本接口警告，更适合自动化调用与跨环境运行。

## PATH 说明

用户级安装通常会把命令安装到：

```bash
~/.local/bin
```

如果安装完成后提示找不到 `aupt`，请将下面内容加入 `~/.bashrc` 或 `~/.zshrc`：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

然后重新打开终端，或执行：

```bash
source ~/.bashrc
```

## 卸载

用户级卸载：

```bash
cd ~/aupt
./scripts/uninstall.sh
```

系统级卸载：

```bash
cd ~/aupt
sudo INSTALL_SCOPE=system ./scripts/uninstall.sh
```

## 受限环境使用

如果你在容器或启用了安全限制的环境中遇到权限问题（如 "no new privileges" 错误），请参考 [受限环境使用指南](RESTRICTED_ENV.md)。

### 快速解决方案

镜像切换等需要修改系统文件的操作，请使用 root 用户运行：

```bash
# 切换到 root 用户
sudo -i

# 执行镜像切换
aupt mirror auto

# 退出 root
exit
```

**注意**: 不要使用 `sudo aupt mirror auto`，在受限环境中可能会失败。

### 不需要 root 权限的功能

以下功能可以直接使用，无需 root 权限：

```bash
aupt doctor          # 系统诊断
aupt mirror list     # 查看镜像列表
aupt search vim      # 搜索包
aupt info vim        # 查看包信息
aupt config show     # 查看配置
```

