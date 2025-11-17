#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误: 当前目录不是 git 仓库${NC}"
    exit 1
fi

# 获取主分支名称（支持 main 或 master）
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$MAIN_BRANCH" ]; then
    # 如果无法自动检测，尝试常见的主分支名称
    if git show-ref --verify --quiet refs/heads/master; then
        MAIN_BRANCH="master"
    elif git show-ref --verify --quiet refs/heads/main; then
        MAIN_BRANCH="main"
    else
        echo -e "${RED}错误: 无法检测主分支名称${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}=== 后端 Feature 分支创建工具 ===${NC}\n"

# 获取新分支名称
if [ -z "$1" ]; then
    echo -e "${YELLOW}请输入 feature 分支名称（不含 feature/ 前缀）:${NC}"
    read -r FEATURE_NAME
else
    FEATURE_NAME="$1"
fi

# 验证分支名称
if [ -z "$FEATURE_NAME" ]; then
    echo -e "${RED}错误: 分支名称不能为空${NC}"
    exit 1
fi

# 构建完整的分支名称
BRANCH_NAME="feature/$FEATURE_NAME"

# 检查分支是否已存在
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    echo -e "${YELLOW}警告: 分支 $BRANCH_NAME 已存在${NC}"
    echo -e "${YELLOW}是否切换到该分支? (y/n)${NC}"
    read -r SWITCH
    if [ "$SWITCH" = "y" ] || [ "$SWITCH" = "Y" ]; then
        git checkout "$BRANCH_NAME"
        echo -e "${GREEN}已切换到分支: $BRANCH_NAME${NC}"
        git status
        exit 0
    else
        exit 0
    fi
fi

# 保存当前未提交的更改
echo -e "${BLUE}1. 检查未提交的更改...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}检测到未提交的更改，正在暂存...${NC}"
    git stash push -m "Auto stash before creating $BRANCH_NAME"
    STASHED=true
else
    STASHED=false
fi

# 切换到主分支
echo -e "\n${BLUE}2. 切换到主分支 ($MAIN_BRANCH)...${NC}"
if ! git checkout "$MAIN_BRANCH"; then
    echo -e "${RED}错误: 无法切换到主分支${NC}"
    exit 1
fi

# 拉取最新代码
echo -e "\n${BLUE}3. 从远程拉取最新代码...${NC}"
if git remote -v | grep -q 'origin'; then
    if ! git pull origin "$MAIN_BRANCH"; then
        echo -e "${RED}错误: 拉取远程代码失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 主分支已更新到最新${NC}"
else
    echo -e "${YELLOW}警告: 未配置远程仓库，跳过拉取${NC}"
fi

# 创建并切换到新分支
echo -e "\n${BLUE}4. 创建新分支: $BRANCH_NAME${NC}"
if ! git checkout -b "$BRANCH_NAME"; then
    echo -e "${RED}错误: 创建分支失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 分支创建成功${NC}"

# 恢复之前暂存的更改
if [ "$STASHED" = true ]; then
    echo -e "\n${BLUE}5. 恢复之前暂存的更改...${NC}"
    git stash pop
fi

# 清理旧的本地分支
echo -e "\n${BLUE}6. 检查可清理的本地分支...${NC}"
# 列出已合并到主分支的本地 feature 分支
MERGED_BRANCHES=$(git branch --merged "$MAIN_BRANCH" | grep "feature/" | grep -v "\*" || true)

if [ -n "$MERGED_BRANCHES" ]; then
    echo -e "${YELLOW}以下分支已合并到 $MAIN_BRANCH:${NC}"
    echo "$MERGED_BRANCHES"
    echo -e "\n${YELLOW}是否删除这些分支? (y/n)${NC}"
    read -r DELETE_MERGED
    if [ "$DELETE_MERGED" = "y" ] || [ "$DELETE_MERGED" = "Y" ]; then
        echo "$MERGED_BRANCHES" | xargs -n 1 git branch -d
        echo -e "${GREEN}✓ 已清理合并的分支${NC}"
    fi
else
    echo -e "${GREEN}✓ 没有需要清理的已合并分支${NC}"
fi

# 显示当前分支状态
echo -e "\n${BLUE}=== 当前分支状态 ===${NC}"
echo -e "${GREEN}当前分支: $(git branch --show-current)${NC}"
echo -e "\n${BLUE}最近的提交:${NC}"
git log -3 --oneline --decorate

echo -e "\n${BLUE}工作区状态:${NC}"
git status -s

echo -e "\n${GREEN}✓ 后端 Feature 分支创建完成！${NC}"
echo -e "${YELLOW}提示: 使用 'git push -u origin $BRANCH_NAME' 推送到远程仓库${NC}"
