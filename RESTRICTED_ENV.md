# 受限环境使用指南

## 问题说明

在某些环境中（如容器、沙箱、或启用了安全限制的系统），可能会遇到以下错误：

```bash
aupt mirror auto
# 错误: The "no new privileges" flag is set, which prevents sudo from running as root.
```

这是因为系统设置了 `NoNewPrivs` 标志，阻止了权限提升（sudo）。

## 检查环境

检查你的环境是否受限：

```bash
cat /proc/self/status | grep NoNewPrivs
# NoNewPrivs: 1  表示受限
# NoNewPrivs: 0  表示正常
```

## 解决方案

### 方案 1: 使用 root 用户运行（推荐）

如果你有 root 访问权限，切换到 root 用户：

```bash
# 方法 A: 使用 sudo -i
sudo -i
aupt mirror auto
exit

# 方法 B: 使用 su
su -
aupt mirror auto
exit
```

**注意**: 不要使用 `sudo aupt mirror auto`，因为在受限环境中，sudo 无法再次调用 sudo。

### 方案 2: 使用手动切换脚本

我们提供了一个手动切换脚本，需要以 root 身份运行：

```bash
# 查看可用镜像
./scripts/manual_mirror_switch.sh

# 切换到清华镜像
sudo -i
cd /path/to/aupt
./scripts/manual_mirror_switch.sh tuna
exit

# 更新索引
sudo apt update
```

### 方案 3: 使用 dry-run 查看并手动编辑

先查看 aupt 会如何修改配置：

```bash
# 查看可用镜像
aupt mirror list

# 查看将要修改的文件（不实际修改）
aupt mirror auto --dry-run
```

然后手动编辑配置文件：

```bash
# 备份原配置
sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup

# 编辑配置文件
sudo nano /etc/apt/sources.list

# 将所有镜像 URL 替换为你选择的镜像
# 例如清华镜像: https://mirrors.tuna.tsinghua.edu.cn/ubuntu

# 更新索引
sudo apt update
```

### 方案 4: 在容器中调整配置

如果你在 Docker 或其他容器中运行，可以调整容器配置：

#### Docker

```bash
# 运行容器时添加 --security-opt 选项
docker run --security-opt no-new-privileges=false your-image

# 或者在 docker-compose.yml 中配置
services:
  your-service:
    security_opt:
      - no-new-privileges:false
```

#### Podman

```bash
# 运行容器时添加 --security-opt 选项
podman run --security-opt no-new-privileges=false your-image
```

## 其他功能的使用

在受限环境中，以下功能仍然可以正常使用：

### ✅ 不需要 root 权限的功能

```bash
# 系统诊断
aupt doctor

# 查看镜像列表
aupt mirror list

# 镜像测速（仅查看，不修改）
aupt mirror auto --dry-run

# 查看配置
aupt config show

# 搜索包（使用 apt-cache，不需要 root）
aupt search vim

# 查看包信息（使用 apt-cache，不需要 root）
aupt info vim

# 性能基准测试
aupt benchmark
```

### ⚠️ 需要 root 权限的功能

以下功能需要以 root 身份运行：

```bash
# 安装包
sudo -i
aupt install vim

# 卸载包
sudo -i
aupt remove vim

# 更新索引
sudo -i
aupt update

# 升级包
sudo -i
aupt upgrade

# 清理缓存
sudo -i
aupt clean

# 切换镜像
sudo -i
aupt mirror auto
```

## 常见问题

### Q: 为什么 `sudo aupt mirror auto` 不工作？

A: 在受限环境中，sudo 本身无法提升权限。aupt 内部尝试再次调用 sudo 时会失败。解决方法是先切换到 root 用户（`sudo -i`），然后直接运行 `aupt mirror auto`。

### Q: 如何恢复原来的镜像配置？

A: aupt 会自动备份原配置为 `.aupt.bak` 后缀：

```bash
sudo cp /etc/apt/sources.list.aupt.bak /etc/apt/sources.list
sudo apt update
```

### Q: 能否让 aupt 不使用 sudo？

A: 镜像切换必须修改 `/etc/apt/sources.list` 等系统文件，这些文件只有 root 才能写入。这是 Linux 系统的安全机制，无法绕过。

### Q: 在容器中使用 aupt 的最佳实践？

A: 建议在 Dockerfile 中以 root 身份运行 aupt：

```dockerfile
FROM ubuntu:22.04

# 安装 aupt
RUN pip install aupt

# 切换镜像（在构建时以 root 身份运行）
RUN aupt mirror switch tuna

# 安装其他包
RUN aupt install vim git
```

## 技术细节

### NoNewPrivs 标志的作用

`NoNewPrivs` 是 Linux 内核的安全特性，用于防止进程获取比父进程更高的权限。当设置为 1 时：

- 无法使用 sudo 提升权限
- 无法使用 setuid 程序
- 无法使用 capabilities

这在容器和沙箱环境中很常见，用于增强安全性。

### 为什么不在 aupt 中内置 root 检查？

aupt 的设计哲学是：
1. 尽可能以普通用户身份运行
2. 只在必要时请求权限
3. 提供清晰的错误信息和解决方案

这样可以：
- 提高安全性（最小权限原则）
- 更好的用户体验（明确告知需要什么权限）
- 更灵活的部署（支持各种环境）

## 相关资源

- [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Podman Security](https://docs.podman.io/en/latest/markdown/podman-run.1.html#security-opt-option)
