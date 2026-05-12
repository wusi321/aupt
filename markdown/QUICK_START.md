# AUPT 快速开始指南

## 🚀 5 分钟快速上手

### 1. 检查系统要求

```bash
# 检查 Python 版本（需要 3.6+）
python3 --version

# 检查系统信息
cat /etc/os-release | grep PRETTY_NAME
```

**支持的系统**:
- ✅ Ubuntu 18.04+ (Python 3.6+)
- ✅ Debian 9+ (Python 3.6+)
- ✅ CentOS 7+ (Python 3.6+)
- ✅ Fedora 35+ (Python 3.10+)
- ✅ Arch Linux (Python 3.11+)

---

### 2. 安装 AUPT

#### 方式 A: 标准安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/wusi321/aupt.git
cd aupt

# 安装
chmod +x scripts/install.sh
./scripts/install.sh
```

#### 方式 B: 兼容性安装（低版本系统）

```bash
cd aupt
chmod +x scripts/install_compat.sh
./scripts/install_compat.sh
```

#### 方式 C: 直接使用 pip

```bash
cd aupt
python3 -m pip install --user .
```

---

### 3. 验证安装

```bash
# 系统诊断
aupt doctor

# 查看可用镜像
aupt mirror list

# 搜索软件包
aupt search vim
```

**预期输出**:
```json
{
  "distro": "Ubuntu 22.04.5 LTS",
  "distro_id": "ubuntu",
  "primary_manager": "apt",
  "available_managers": ["apt", "snap"]
}
```

---

### 4. 基本使用

#### 查询操作（无需 root）

```bash
# 搜索包
aupt search nginx

# 查看包信息
aupt info python3

# 查看配置
aupt config show

# 查看镜像列表
aupt mirror list
```

#### 管理操作（需要 root）

```bash
# 切换到 root 用户
sudo -i

# 安装包
aupt install vim

# 卸载包
aupt remove gcc

# 更新索引
aupt update

# 升级包
aupt upgrade

# 切换镜像
aupt mirror auto

# 退出 root
exit
```

---

### 5. 常用场景

#### 场景 1: 切换到最快镜像

```bash
# 查看可用镜像
aupt mirror list

# 自动选择最快镜像（需要 root）
sudo -i
aupt mirror auto
exit

# 更新索引
sudo apt update
```

#### 场景 2: 安装软件

```bash
# 搜索软件
aupt search redis

# 查看信息
aupt info redis

# 安装（需要 root）
sudo -i
aupt install redis
exit
```

#### 场景 3: 系统诊断

```bash
# 运行诊断
aupt doctor

# 查看配置
aupt config show

# 查看可用包管理器
aupt doctor | grep available_managers
```

---

## 📚 进阶使用

### 指定包管理器

```bash
# 强制使用 apt
aupt apt install vim

# 强制使用 snap
aupt snap install code

# 强制使用 flatpak
aupt flatpak install org.gimp.GIMP
```

### 版本控制

```bash
# 安装指定版本
aupt install gcc==9
aupt install python@3.10
```

### Dry-run 模式

```bash
# 预览命令（不实际执行）
aupt install vim --dry-run
aupt mirror auto --dry-run
```

### 配置管理

```bash
# 查看所有配置
aupt config show

# 获取单个配置
aupt config get mirror.timeout

# 设置配置
aupt config set mirror.timeout 5.0
```

---

## 🔧 故障排除

### 问题 1: 找不到 aupt 命令

**原因**: PATH 未配置

**解决**:
```bash
# 添加到 PATH
export PATH="$HOME/.local/bin:$PATH"

# 永久生效
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 问题 2: Python 版本太低

**原因**: 系统 Python < 3.6

**解决**:
```bash
# Ubuntu 16.04
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.6 python3.6-pip
PYTHON_BIN=python3.6 ./scripts/install.sh

# CentOS 7
sudo yum install epel-release
sudo yum install python36 python36-pip
PYTHON_BIN=python3.6 ./scripts/install.sh
```

### 问题 3: 权限错误

**原因**: 在受限环境中使用 sudo

**解决**:
```bash
# ✅ 正确方式
sudo -i
aupt mirror auto
exit

# ❌ 错误方式
sudo aupt mirror auto  # 在受限环境中会失败
```

### 问题 4: 安装失败

**原因**: 缺少依赖或网络问题

**解决**:
```bash
# 使用兼容性安装脚本
./scripts/install_compat.sh

# 或手动安装依赖
python3 -m pip install --user setuptools wheel
python3 -m pip install --user .
```

---

## 📖 更多资源

### 文档

- [README.md](../README.md) - 完整文档
- [COMPATIBILITY.md](COMPATIBILITY.md) - 版本兼容性
- [RESTRICTED_ENV.md](RESTRICTED_ENV.md) - 受限环境指南
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 命令速查

### 命令参考

| 命令 | 说明 | 需要 root |
|------|------|----------|
| `aupt doctor` | 系统诊断 | ❌ |
| `aupt search <keyword>` | 搜索包 | ❌ |
| `aupt info <package>` | 查看包信息 | ❌ |
| `aupt mirror list` | 查看镜像 | ❌ |
| `aupt config show` | 查看配置 | ❌ |
| `aupt install <package>` | 安装包 | ✅ |
| `aupt remove <package>` | 卸载包 | ✅ |
| `aupt update` | 更新索引 | ✅ |
| `aupt upgrade` | 升级包 | ✅ |
| `aupt mirror auto` | 切换镜像 | ✅ |
| `aupt clean` | 清理缓存 | ✅ |

---

## 💡 最佳实践

### 1. 定期更新

```bash
sudo -i
aupt update
aupt upgrade
exit
```

### 2. 使用最快镜像

```bash
# 每月运行一次
sudo -i
aupt mirror auto
exit
```

### 3. 搜索前先查询

```bash
# 先搜索
aupt search redis

# 再查看信息
aupt info redis-server

# 最后安装
sudo -i
aupt install redis-server
exit
```

### 4. 使用 dry-run 预览

```bash
# 预览将要执行的命令
aupt install vim --dry-run
aupt mirror auto --dry-run
```

---

## 🎯 下一步

1. ✅ 完成安装
2. ✅ 运行 `aupt doctor` 验证
3. ✅ 尝试搜索和查询功能
4. ✅ 切换到最快镜像
5. ✅ 安装常用软件

**恭喜！你已经掌握了 AUPT 的基本使用！** 🎉

---

## 📞 获取帮助

- 查看文档：[README.md](../README.md)
- 运行诊断：`aupt doctor`
- 查看日志：`cat ~/.aupt/aupt.log`
- 提交 Issue：[GitHub Issues](https://github.com/wusi321/aupt/issues)

---

**版本**: 0.1.0  
**更新**: 2026-05-12
