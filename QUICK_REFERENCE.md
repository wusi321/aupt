# AUPT 快速参考

## 安装

```bash
cd ~/aupt
./scripts/install.sh
```

## 卸载

```bash
cd ~/aupt
./scripts/uninstall.sh
```

---

## 常用命令

### 📦 包管理（需要 root）

```bash
# 切换到 root 用户
sudo -i

# 安装包
aupt install vim

# 卸载包
aupt remove vim

# 更新索引
aupt update

# 升级所有包
aupt upgrade

# 清理缓存
aupt clean

# 退出 root
exit
```

### 🔍 查询（无需 root）

```bash
# 搜索包
aupt search vim

# 查看包信息
aupt info vim

# 系统诊断
aupt doctor
```

### 🌐 镜像管理

```bash
# 查看可用镜像（无需 root）
aupt mirror list

# 预览镜像切换（无需 root）
aupt mirror auto --dry-run

# 自动选择最快镜像（需要 root）
sudo -i
aupt mirror auto
exit

# 切换到指定镜像（需要 root）
sudo -i
aupt mirror switch tuna
exit
```

### ⚙️ 配置管理（无需 root）

```bash
# 查看配置
aupt config show

# 获取配置项
aupt config get mirror.timeout

# 设置配置项
aupt config set mirror.timeout 5.0
```

---

## 可用镜像

| 名称 | 说明 |
|------|------|
| official | Ubuntu 官方源 |
| tuna | 清华大学镜像 |
| ustc | 中国科学技术大学镜像 |
| aliyun | 阿里云镜像 |

---

## 受限环境使用

### 问题诊断

```bash
# 检查是否在受限环境
cat /proc/self/status | grep NoNewPrivs
# NoNewPrivs: 1  表示受限
```

### 解决方案

```bash
# ✅ 正确方式：先切换到 root
sudo -i
aupt mirror auto
exit

# ❌ 错误方式：直接使用 sudo
sudo aupt mirror auto  # 在受限环境中会失败
```

---

## 指定包管理器

```bash
# 强制使用 apt
aupt apt install vim

# 强制使用 snap
aupt snap install code

# 强制使用 flatpak
aupt flatpak install org.gimp.GIMP
```

---

## 版本控制

```bash
# 安装指定版本
aupt install gcc==9
aupt install python@3.10
```

---

## Dry-run 模式

所有修改操作都支持 dry-run（仅显示命令，不执行）：

```bash
aupt install vim --dry-run
aupt remove gcc --dry-run
aupt mirror auto --dry-run
```

---

## 常见问题

### Q: 为什么 `sudo aupt mirror auto` 不工作？

A: 在受限环境中，使用 `sudo -i` 先切换到 root 用户：

```bash
sudo -i
aupt mirror auto
exit
```

### Q: 如何恢复原来的镜像配置？

A: aupt 会自动备份为 `.aupt.bak`：

```bash
sudo cp /etc/apt/sources.list.aupt.bak /etc/apt/sources.list
sudo apt update
```

### Q: 哪些命令需要 root 权限？

A: 
- ✅ 无需 root: `doctor`, `search`, `info`, `mirror list`, `config`
- ⚠️ 需要 root: `install`, `remove`, `update`, `upgrade`, `clean`, `mirror auto/switch`

---

## 获取帮助

```bash
# 查看系统状态
aupt doctor

# 查看配置
aupt config show

# 查看日志
cat ~/.aupt/aupt.log
```

---

## 相关文档

- [README.md](README.md) - 完整文档
- [RESTRICTED_ENV.md](RESTRICTED_ENV.md) - 受限环境使用指南
- [BUGFIX.md](BUGFIX.md) - Bug 修复说明
- [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md) - 问题解决方案总结

---

## 快速示例

### 示例 1: 安装软件

```bash
sudo -i
aupt install vim git gcc
exit
```

### 示例 2: 切换镜像

```bash
# 查看可用镜像
aupt mirror list

# 切换到清华镜像
sudo -i
aupt mirror switch tuna
exit

# 更新索引
sudo apt update
```

### 示例 3: 搜索和查看信息

```bash
# 搜索 Python 相关包
aupt search python

# 查看 Python 包信息
aupt info python3
```

### 示例 4: 系统诊断

```bash
aupt doctor
```

输出示例：
```json
{
  "distro": "Ubuntu 22.04.5 LTS",
  "distro_id": "ubuntu",
  "id_like": ["debian"],
  "primary_manager": "apt",
  "available_managers": ["apt", "snap"],
  "config_path": "/home/user/.config/aupt/config.yaml"
}
```
