# Bug 修复说明

## 修复的问题

### 1. 卸载脚本错误 (scripts/uninstall.sh)

**问题描述:**
```bash
./uninstall.sh
# 错误: no such option: --user
```

**原因分析:**
`pip uninstall` 命令不支持 `--user` 选项。pip 会自动检测包的安装位置并卸载，无需指定 `--user`。

**修复方案:**
移除了 `build_uninstall_args()` 函数中的 `--user` 选项，统一使用 `pip uninstall -y aupt`。

**修复后的代码:**
```bash
build_uninstall_args() {
  printf '%s\n' "aupt"
}
```

---

### 2. 镜像切换权限错误 (aupt/core/mirror_manager.py)

**问题描述:**
```bash
aupt mirror auto
# 错误: PermissionError: [Errno 13] Permission denied: '/etc/apt/sources.list.aupt.bak'
```

**原因分析:**
镜像切换功能需要修改 `/etc/apt/sources.list` 等系统配置文件，这些文件需要 root 权限才能写入。原代码直接使用 Python 的 `Path.write_text()` 方法，没有使用 `sudo` 提权。

**修复方案:**
1. 新增 `_write_mirror_config()` 方法，使用 `sudo cp` 命令写入系统文件
2. 使用临时文件作为中转，避免直接写入系统目录
3. 先备份原文件，再写入新内容
4. 添加错误处理和清理逻辑

**修复后的流程:**
```
1. 创建临时文件保存备份内容
2. 创建临时文件保存新内容
3. 使用 sudo cp 将备份写入 /etc/apt/sources.list.aupt.bak
4. 使用 sudo cp 将新内容写入 /etc/apt/sources.list
5. 清理临时文件
```

**关键代码:**
```python
def _write_mirror_config(self, path: Path, original: str, updated: str) -> CommandResult:
    """使用 sudo 写入系统文件"""
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as backup_tmp:
        backup_tmp.write(original)
    
    # 使用 sudo cp 写入
    subprocess.run(["sudo", "cp", backup_tmp_path, str(backup_path)])
    subprocess.run(["sudo", "cp", content_tmp_path, str(path)])
```

---

## 测试验证

### 测试 1: 卸载功能
```bash
./scripts/uninstall.sh
# ✅ 成功: AUPT 卸载完成
```

### 测试 2: 安装功能
```bash
./scripts/install.sh
# ✅ 成功: AUPT 安装完成
```

### 测试 3: 系统诊断
```bash
aupt doctor
# ✅ 成功: 显示系统信息
```

### 测试 4: 镜像列表
```bash
aupt mirror list
# ✅ 成功: 显示可用镜像
```

### 测试 5: 镜像切换 (dry-run)
```bash
aupt mirror auto --dry-run
# ✅ 成功: 显示将要修改的文件
```

### 测试 6: 镜像切换 (实际执行)
```bash
aupt mirror auto
# ✅ 成功: 需要 sudo 权限，会提示输入密码
```

---

## 使用说明

### 镜像切换功能

镜像切换需要修改系统文件，因此会要求 sudo 权限：

```bash
# 自动选择最快镜像
aupt mirror auto
# 系统会提示输入 sudo 密码

# 切换到指定镜像
aupt mirror switch tuna

# 仅查看不修改（dry-run）
aupt mirror auto --dry-run
```

### 备份说明

每次切换镜像时，原配置文件会自动备份为 `.aupt.bak` 后缀：
- `/etc/apt/sources.list` → `/etc/apt/sources.list.aupt.bak`

如需恢复原配置：
```bash
sudo cp /etc/apt/sources.list.aupt.bak /etc/apt/sources.list
```

---

## 技术细节

### 为什么使用 sudo cp 而不是 sudo python?

1. **安全性**: 避免以 root 权限运行整个 Python 进程
2. **最小权限原则**: 只在必要的文件操作时提权
3. **兼容性**: 不依赖 Python 的 sudo 环境配置

### 临时文件的作用

使用临时文件可以：
1. 避免在系统目录创建临时文件（可能没有权限）
2. 确保内容完整写入后再复制到目标位置
3. 便于清理和错误恢复

---

## 相关文件

- `scripts/uninstall.sh` - 卸载脚本
- `aupt/core/mirror_manager.py` - 镜像管理模块
- `aupt/utils/subprocess_wrapper.py` - 命令执行封装

---

## 后续优化建议

1. **PolicyKit 集成**: 考虑使用 PolicyKit 实现更细粒度的权限控制
2. **配置验证**: 在写入前验证配置文件语法
3. **回滚机制**: 如果切换失败，自动恢复备份
4. **镜像测速缓存**: 缓存测速结果，避免频繁测试
