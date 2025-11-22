# 脚本目录

本目录包含项目开发和管理相关的辅助脚本。

## 📁 脚本列表

### Git 工作流脚本

这些脚本帮助简化 Git 操作流程：

#### `git-commit.sh`
执行标准化的 Git 提交

**用法**：
```bash
./scripts/git-commit.sh
```

功能：
- 显示当前修改状态
- 提示输入提交类型和消息
- 执行 git add 和 git commit

#### `merge-to-main.sh`
将当前分支合并到主分支

**用法**：
```bash
./scripts/merge-to-main.sh
```

功能：
- 检查当前分支状态
- 切换到主分支并拉取最新代码
- 合并当前分支
- 推送到远程仓库

## 🚀 使用前准备

### Linux/macOS

添加执行权限：
```bash
chmod +x scripts/*.sh
```

### Windows

使用 Git Bash 或 WSL 运行这些脚本。

## 📝 注意事项

1. **运行位置**: 这些脚本应该从项目根目录运行
2. **Git 配置**: 确保已配置 Git 用户名和邮箱
3. **权限**: 确保脚本有执行权限（Linux/macOS）

## 🔧 自定义脚本

你可以根据项目需求修改或添加新的脚本到此目录。

## 💡 最佳实践

- 使用 `git-commit.sh` 进行规范化提交
- 使用 `merge-to-main.sh` 安全合并代码

---

这些脚本旨在简化开发工作流程，提高开发效率。
