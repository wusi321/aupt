# AUPT

AUPT--一个统一的 Linux 包管理调度工具：

# **AUPT (Advanced Unified Package Tool)**

核心目标：

```text
统一命令入口 + 自动识别发行版 + 自动选择包管理器
```

---

## 3. 核心功能目标（Feature Goals）

### 3.1 基础功能

- 自动识别 Linux 发行版
- 自动调用系统对应包管理器
- 支持统一安装命令
- 支持统一卸载命令
- 支持统一更新命令

示例：

```bash
aupt install vim
aupt remove gcc
aupt update
aupt upgrade
```

---

### 3.2 指定包管理器

支持用户强制指定工具：

```bash
aupt apt install nginx
aupt pacman install git
aupt snap install code
```

---

### 3.3 自动包管理器选择策略

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

### 3.4 版本控制支持

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

### 3.5 镜像源自动优化

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

### 3.6 包搜索与信息查询

```bash
aupt search redis
aupt info nodejs
```

---

### 3.7 系统诊断功能

```bash
aupt doctor
```

用于检测：

- 包管理器状态
- 网络状态
- 镜像源状态

---

## 4. 系统总体架构（System Architecture）

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
```

---

## 5. CLI 设计规范（Command Interface）

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


## 安装

### 方式一：使用安装脚本

默认执行用户级安装，使用系统 `python3`：

```bash
git clone git@github.com:wusi321/aupt.git
cd ~/aupt
chmod +x scripts/install.sh scripts/uninstall.sh
./scripts/install.sh
```

安装完成后，命令会通过 `console_script` 暴露为全局可执行命令：

```bash
aupt doctor
aupt install vim --dry-run
```

### 方式二：直接使用 `pip`

仍然使用系统 `python3`：

```bash
cd ~/aupt
python3 -m pip install --user .
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

