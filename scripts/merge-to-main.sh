#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误: 当前目录不是 git 仓库${NC}"
    exit 1
fi

# 检查是否安装了 gh 命令
if ! command -v gh &> /dev/null; then
    echo -e "${RED}错误: 未安装 GitHub CLI (gh)${NC}"
    echo -e "${YELLOW}请访问 https://cli.github.com/ 安装 gh 命令${NC}"
    exit 1
fi

echo -e "${BLUE}=== 后端分支合并工具 ===${NC}\n"

# 获取当前分支名称
CURRENT_BRANCH=$(git branch --show-current)

if [ -z "$CURRENT_BRANCH" ]; then
    echo -e "${RED}错误: 无法获取当前分支名称${NC}"
    exit 1
fi

echo -e "${CYAN}当前分支: ${CURRENT_BRANCH}${NC}"

# 获取主分支名称（支持 main 或 master）
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$MAIN_BRANCH" ]; then
    # 如果无法自动检测，尝试常见的主分支名称
    if git show-ref --verify --quiet refs/heads/master; then
        MAIN_BRANCH="master"
    elif git show-ref --verify --quiet refs/heads/main; then
        MAIN_BRANCH="main"
    el
    else
        echo -e "${RED}错误: 无法检测主分支名称${NC}"
        exit 1
    fi
fi

echo -e "${CYAN}目标分支: ${MAIN_BRANCH}${NC}\n"

# 检查是否在主分支上
if [ "$CURRENT_BRANCH" = "$MAIN_BRANCH" ]; then
    echo -e "${RED}错误: 当前已在主分支 ${MAIN_BRANCH} 上，无需创建合并请求${NC}"
    exit 1
fi

# 检查是否有未提交的更改
echo -e "${BLUE}1. 检查工作区状态...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}警告: 检测到未提交的更改${NC}"
    git status -s
    echo -e "\n${YELLOW}是否提交这些更改? (y/n)${NC}"
    read -r COMMIT_CHANGES

    if [ "$COMMIT_CHANGES" = "y" ] || [ "$COMMIT_CHANGES" = "Y" ]; then
        echo -e "${YELLOW}请输入提交信息:${NC}"
        read -r COMMIT_MESSAGE

        if [ -z "$COMMIT_MESSAGE" ]; then
            echo -e "${RED}错误: 提交信息不能为空${NC}"
            exit 1
        fi

        git add .
        git commit -m "$COMMIT_MESSAGE

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
        echo -e "${GREEN}✓ 更改已提交${NC}"
    else
        echo -e "${YELLOW}请先提交或暂存更改，然后重新运行此脚本${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 工作区干净${NC}"
fi

# 推送当前分支到远程
echo -e "\n${BLUE}2. 推送分支到远程...${NC}"
if git remote -v | grep -q 'origin'; then
    # 检查远程分支是否存在
    if git ls-remote --heads origin "$CURRENT_BRANCH" | grep -q "$CURRENT_BRANCH"; then
        # 远程分支存在，直接推送
        if git push origin "$CURRENT_BRANCH"; then
            echo -e "${GREEN}✓ 分支已推送到远程${NC}"
        else
            echo -e "${RED}错误: 推送失败${NC}"
            exit 1
        fi
    else
        # 远程分支不存在，使用 -u 创建跟踪
        if git push -u origin "$CURRENT_BRANCH"; then
            echo -e "${GREEN}✓ 分支已推送到远程${NC}"
        else
            echo -e "${RED}错误: 推送失败${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}错误: 未配置远程仓库${NC}"
    exit 1
fi

# 获取分支的所有提交记录
echo -e "\n${BLUE}3. 分析分支更改...${NC}"
COMMIT_COUNT=$(git rev-list --count "$MAIN_BRANCH".."$CURRENT_BRANCH" 2>/dev/null || echo "0")
echo -e "${CYAN}提交数量: ${COMMIT_COUNT}${NC}"

# 显示最近的提交
if [ "$COMMIT_COUNT" -gt "0" ]; then
    echo -e "\n${CYAN}最近的提交:${NC}"
    git log --oneline "$MAIN_BRANCH".."$CURRENT_BRANCH" | head -5
fi

# 生成 PR 标题和描述
echo -e "\n${BLUE}4. 创建 Pull Request...${NC}"

# 自动生成 PR 标题（基于分支名）
PR_TITLE=$(echo "$CURRENT_BRANCH" | sed 's/feature\///' | sed 's/bugfix\///' | sed 's/hotfix\///' | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

# 生成 PR 描述
PR_BODY="## 📝 更改概述

本 PR 包含 ${COMMIT_COUNT} 个提交的更改。

## 🔧 更改内容

$(git log --format='- %s' "$MAIN_BRANCH".."$CURRENT_BRANCH" | head -10)

## ✅ 测试清单

- [ ] 代码已在本地测试
- [ ] 单元测试已通过
- [ ] 代码符合项目规范
- [ ] 已更新相关文档

## 📌 相关链接

<!-- 如有相关 Issue，请在此添加链接 -->

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

# 询问是否要自定义 PR 信息
echo -e "${YELLOW}使用自动生成的 PR 标题和描述? (y/n)${NC}"
echo -e "${CYAN}标题: ${PR_TITLE}${NC}"
read -r USE_AUTO

if [ "$USE_AUTO" = "n" ] || [ "$USE_AUTO" = "N" ]; then
    echo -e "${YELLOW}请输入 PR 标题:${NC}"
    read -r CUSTOM_TITLE
    if [ -n "$CUSTOM_TITLE" ]; then
        PR_TITLE="$CUSTOM_TITLE"
    fi
fi

# 创建 Pull Request
if gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base "$MAIN_BRANCH" --head "$CURRENT_BRANCH"; then
    echo -e "\n${GREEN}✓ Pull Request 创建成功！${NC}"

    # 获取 PR URL
    PR_URL=$(gh pr view --json url -q .url 2>/dev/null)
    if [ -n "$PR_URL" ]; then
        echo -e "${CYAN}PR 链接: ${PR_URL}${NC}"
    fi

    # 显示 PR 状态
    echo -e "\n${BLUE}=== Pull Request 状态 ===${NC}"
    gh pr view

else
    echo -e "${RED}错误: 创建 Pull Request 失败${NC}"
    echo -e "${YELLOW}提示: 请检查是否已登录 GitHub CLI (gh auth login)${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ 合并请求已提交！${NC}"
echo -e "${YELLOW}提示: 请在 GitHub 上等待代码审查并完成合并${NC}"
