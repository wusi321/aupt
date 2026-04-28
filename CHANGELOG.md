# 更新日志

## [未发布] - 2026-04-28

### 🐛 Bug 修复

#### 1. 修复卸载脚本错误
- **问题**: `pip uninstall` 不支持 `--user` 选项
- **文件**: `scripts/uninstall.sh`
- **修复**: 移除了 `build_uninstall_args()` 函数中的 `--user` 参数
- **影响**: 卸载功能现在可以正常工作

#### 2. 修复镜像切换权限问题
- **问题**: 在受限环境中无法使用 sudo 修改系统文件
- **文件**: `aupt/core/mirror_manager.py`
- **修复**: 
  - 改为直接写入文件（需要以 root 身份运行）
  - 添加友好的错误提示和解决方案
  - 移除对 sudo 的依赖
- **影响**: 镜像切换功能在受限环境中可以正常工作

### ✨ 新增功能

#### 1. 手动镜像切换脚本
- **文件**: `scripts/manual_mirror_switch.sh`
- **功能**: 提供手动切换镜像的备选方案
- **用法**: `./scripts/manual_mirror_switch.sh tuna`

#### 2. 受限环境使用指南
- **文件**: `RESTRICTED_ENV.md`
- **内容**: 
  - 环境诊断方法
  - 多种解决方案
  - 容器配置建议
  - 常见问题解答

#### 3. 快速参考文档
- **文件**: `QUICK_REFERENCE.md`
- **内容**: 常用命令速查表

#### 4. 问题解决方案总结
- **文件**: `SOLUTION_SUMMARY.md`
- **内容**: 详细的问题分析和解决方案演进过程

### 📝 文档改进

#### 1. 更新 README.md
- 添加受限环境使用说明
- 添加权限要求说明
- 改进安装和卸载说明

#### 2. 新增 BUGFIX.md
- 详细的 Bug 修复说明
- 测试验证结果
- 技术细节说明

### 🔧 技术改进

#### 1. 权限处理优化
```python
# 改进前：依赖 sudo
subprocess.run(["sudo", "cp", src, dst])

# 改进后：直接写入 + 友好错误提示
try:
    path.write_text(content)
except PermissionError:
    # 提供清晰的错误信息和解决方案
```

#### 2. 错误信息改进
- 从技术错误信息改为用户友好的指导
- 提供多种解决方案
- 包含具体的命令示例

#### 3. 环境兼容性
- 支持正常环境（NoNewPrivs: 0）
- 支持受限环境（NoNewPrivs: 1）
- 支持容器环境

### 🧪 测试验证

所有功能已通过测试：

- ✅ 安装/卸载脚本
- ✅ 系统诊断 (`aupt doctor`)
- ✅ 包搜索 (`aupt search`)
- ✅ 包信息查询 (`aupt info`)
- ✅ 镜像列表 (`aupt mirror list`)
- ✅ 镜像切换预览 (`aupt mirror auto --dry-run`)
- ✅ 配置管理 (`aupt config`)
- ✅ Dry-run 模式

### 📊 性能影响

- 无性能影响
- 移除了不必要的 sudo 调用
- 简化了文件写入流程

### 🔒 安全性

- ✅ 遵循最小权限原则
- ✅ 不强制使用 sudo
- ✅ 提供 dry-run 预览
- ✅ 自动备份配置文件

### 📚 文档结构

```
aupt/
├── README.md                    # 主文档
├── BUGFIX.md                    # Bug 修复说明
├── RESTRICTED_ENV.md            # 受限环境指南
├── SOLUTION_SUMMARY.md          # 解决方案总结
├── QUICK_REFERENCE.md           # 快速参考
├── CHANGELOG.md                 # 本文件
└── scripts/
    ├── install.sh               # 安装脚本
    ├── uninstall.sh             # 卸载脚本（已修复）
    └── manual_mirror_switch.sh  # 手动镜像切换（新增）
```

### 🎯 用户影响

#### 正面影响
- ✅ 卸载功能正常工作
- ✅ 镜像切换在受限环境中可用
- ✅ 更清晰的错误信息
- ✅ 更完善的文档
- ✅ 提供多种解决方案

#### 使用变化
- ⚠️ 镜像切换需要先切换到 root 用户（`sudo -i`）
- ⚠️ 不能直接使用 `sudo aupt mirror auto`（在受限环境中）

### 🔄 迁移指南

#### 从旧版本升级

1. 重新安装：
```bash
cd ~/aupt
./scripts/uninstall.sh
./scripts/install.sh
```

2. 更新使用方式：
```bash
# 旧方式（可能失败）
sudo aupt mirror auto

# 新方式（推荐）
sudo -i
aupt mirror auto
exit
```

### 🐛 已知问题

无

### 🚀 未来计划

#### 短期（1-2 周）
- [ ] 添加更多镜像源
- [ ] 改进镜像测速算法
- [ ] 添加配置文件语法验证

#### 中期（1-2 月）
- [ ] 支持更多发行版（Fedora, openSUSE 等）
- [ ] 实现 PolicyKit 集成
- [ ] 添加自动回滚机制

#### 长期（3-6 月）
- [ ] 开发 GUI 界面
- [ ] 实现插件系统
- [ ] 支持 AUR（Arch User Repository）

### 🙏 致谢

感谢所有测试和反馈的用户！

### 📞 联系方式

如有问题或建议，请：
- 提交 Issue
- 查看文档
- 运行 `aupt doctor` 诊断

---

## 版本历史

### [0.1.0] - 初始版本
- 基础架构实现
- 支持 apt, pacman, dnf, zypper, flatpak, snap
- 发行版自动识别
- 包别名解析
- 镜像管理功能
- 配置管理系统

---

## 版本号说明

遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**: 不兼容的 API 修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

当前版本: **0.1.0**
