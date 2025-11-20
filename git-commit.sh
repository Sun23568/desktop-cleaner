#!/bin/bash

# Git 约定式提交脚本
# 支持中文输入，符合 Conventional Commits 规范

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
COMMIT_TYPE=""
COMMIT_SCOPE=""
COMMIT_DESCRIPTION=""
COMMIT_BODY=""
COMMIT_FOOTER=""
IS_BREAKING="false"

# 打印带颜色的标题
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}   Git 约定式提交助手${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 检查并处理工作区文件
check_and_stage_files() {
    echo -e "\n${BLUE}1. 检查工作区状态...${NC}"

    # 检查是否有任何更改（包括未跟踪的文件）
    if git status --short | grep -q '^'; then
        echo -e "${YELLOW}检测到以下更改:${NC}\n"
        git status --short

        echo -e "\n${YELLOW}是否将所有更改添加到暂存区? (y/n):${NC}"
        read -r add_all

        if [[ "$add_all" =~ ^[Yy]$ ]]; then
            git add .
            echo -e "${GREEN}✓ 所有更改已添加到暂存区${NC}"
        else
            echo -e "${YELLOW}请手动选择要添加的文件:${NC}"
            echo -e "${CYAN}提示: 使用 'git add <文件>' 命令${NC}"
            return 1
        fi
    fi

    # 再次检查是否有暂存的文件
    if ! git diff --cached --quiet; then
        echo -e "${GREEN}✓ 检测到已暂存的文件${NC}\n"
        echo -e "${CYAN}将要提交的文件:${NC}"
        git diff --cached --name-status
        return 0
    else
        echo -e "${RED}错误: 没有文件被暂存，无法提交${NC}"
        return 1
    fi
}

# 显示提交类型选项
show_type_options() {
    echo -e "\n${BLUE}2. 选择提交类型${NC}"
    echo -e "${YELLOW}请选择提交类型:${NC}"
    echo "  1) feat     - 新功能"
    echo "  2) fix      - 修复 bug"
    echo "  3) docs     - 文档更新"
    echo "  4) style    - 代码格式调整(不影响功能)"
    echo "  5) refactor - 重构代码"
    echo "  6) perf     - 性能优化"
    echo "  7) test     - 测试相关"
    echo "  8) build    - 构建系统或外部依赖"
    echo "  9) ci       - CI/CD 配置"
    echo " 10) chore    - 其他杂项"
    echo " 11) revert   - 回退之前的提交"
}

# 获取提交类型
get_commit_type() {
    while true; do
        echo -e "${YELLOW}输入数字选择 [1-11]: ${NC}"
        read -r choice
        case $choice in
            1) COMMIT_TYPE="feat"; return 0;;
            2) COMMIT_TYPE="fix"; return 0;;
            3) COMMIT_TYPE="docs"; return 0;;
            4) COMMIT_TYPE="style"; return 0;;
            5) COMMIT_TYPE="refactor"; return 0;;
            6) COMMIT_TYPE="perf"; return 0;;
            7) COMMIT_TYPE="test"; return 0;;
            8) COMMIT_TYPE="build"; return 0;;
            9) COMMIT_TYPE="ci"; return 0;;
            10) COMMIT_TYPE="chore"; return 0;;
            11) COMMIT_TYPE="revert"; return 0;;
            *) echo -e "${RED}无效选择，请输入 1-11 之间的数字${NC}";;
        esac
    done
}

# 获取作用域(可选)
get_scope() {
    echo -e "\n${BLUE}3. 设置作用域 (可选)${NC}"
    echo -e "${YELLOW}请输入作用域 (直接回车跳过):${NC}"
    echo -e "${CYAN}提示: 例如 api, ui, database, auth 等${NC}"
    read -r COMMIT_SCOPE
}

# 获取简短描述
get_description() {
    echo -e "\n${BLUE}4. 填写提交描述${NC}"
    while true; do
        echo -e "${YELLOW}请输入简短描述 (必填):${NC}"
        echo -e "${CYAN}提示: 用一句话说明此次提交的主要内容${NC}"
        read -r COMMIT_DESCRIPTION
        if [ -n "$COMMIT_DESCRIPTION" ]; then
            return 0
        else
            echo -e "${RED}描述不能为空，请重新输入${NC}"
        fi
    done
}

# 是否为破坏性变更
get_breaking_change() {
    echo -e "\n${YELLOW}这是一个破坏性变更吗? (y/n):${NC}"
    read -r breaking
    if [[ "$breaking" =~ ^[Yy]$ ]]; then
        IS_BREAKING="true"
    else
        IS_BREAKING="false"
    fi
}

# 获取详细说明(可选)
get_body() {
    echo -e "\n${BLUE}5. 添加详细说明 (可选)${NC}"
    echo -e "${YELLOW}请输入详细说明 (直接回车跳过):${NC}"
    echo -e "${CYAN}提示: 可以详细说明改动原因、方案等${NC}"
    echo -e "${CYAN}多行输入时，输入单独一行的句点 '.' 结束输入${NC}"

    # 读取第一行
    read -r first_line

    # 如果第一行为空，跳过详细说明
    if [ -z "$first_line" ]; then
        COMMIT_BODY=""
        return 0
    fi

    # 如果第一行就是句点，跳过详细说明
    if [ "$first_line" = "." ]; then
        COMMIT_BODY=""
        return 0
    fi

    # 第一行有内容，继续读取
    COMMIT_BODY="$first_line"
    while IFS= read -r line; do
        if [ "$line" = "." ]; then
            break
        fi
        COMMIT_BODY="$COMMIT_BODY"$'\n'"$line"
    done
}

# 获取页脚(可选)
get_footer() {
    echo -e "\n${BLUE}6. 添加页脚信息 (可选)${NC}"
    echo -e "${YELLOW}请输入页脚信息 (直接回车跳过):${NC}"
    echo -e "${CYAN}提示: 例如 'Closes #123' 或 'BREAKING CHANGE: xxx'${NC}"
    read -r COMMIT_FOOTER
}

# 构建提交信息
build_commit_message() {
    local message="$COMMIT_TYPE"

    # 添加作用域
    if [ -n "$COMMIT_SCOPE" ]; then
        message="$message($COMMIT_SCOPE)"
    fi

    # 添加破坏性变更标记
    if [ "$IS_BREAKING" = "true" ]; then
        message="$message!"
    fi

    # 添加描述
    message="$message: $COMMIT_DESCRIPTION"

    # 添加详细说明
    if [ -n "$COMMIT_BODY" ]; then
        message="$message"$'\n\n'"$COMMIT_BODY"
    fi

    # 添加页脚
    if [ -n "$COMMIT_FOOTER" ]; then
        if [ -n "$COMMIT_BODY" ]; then
            message="$message"$'\n\n'"$COMMIT_FOOTER"
        else
            message="$message"$'\n\n'"$COMMIT_FOOTER"
        fi
    fi

    echo "$message"
}

# 显示预览并确认
preview_and_confirm() {
    local message=$1

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}7. 提交信息预览${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "$message"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -e "\n${YELLOW}确认提交? (y/n):${NC}"
    read -r confirm

    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# 主函数
main() {
    print_header

    # 检查是否在 git 仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}错误: 当前目录不是 Git 仓库${NC}"
        exit 1
    fi

    # 检查并处理工作区文件
    if ! check_and_stage_files; then
        echo -e "\n${BLUE}已取消${NC}"
        exit 0
    fi

    # 收集提交信息
    show_type_options
    get_commit_type

    get_scope
    get_description
    get_breaking_change
    get_body
    get_footer

    # 构建提交信息
    commit_message=$(build_commit_message)

    # 预览并确认
    if preview_and_confirm "$commit_message"; then
        if git commit -m "$commit_message"; then
            echo -e "\n${GREEN}✓ 提交成功!${NC}"

            # 显示提交信息
            echo -e "\n${CYAN}最新提交:${NC}"
            git log -1 --oneline

            # 询问是否推送到远程
            echo -e "\n${YELLOW}是否推送到远程仓库? (y/n):${NC}"
            read -r push_choice

            if [[ "$push_choice" =~ ^[Yy]$ ]]; then
                current_branch=$(git branch --show-current)
                if git push origin "$current_branch"; then
                    echo -e "${GREEN}✓ 推送成功!${NC}"
                else
                    echo -e "${YELLOW}推送失败，可能需要先设置上游分支:${NC}"
                    echo -e "${CYAN}git push -u origin $current_branch${NC}"
                fi
            fi
        else
            echo -e "\n${RED}✗ 提交失败${NC}"
            exit 1
        fi
    else
        echo -e "\n${BLUE}已取消提交${NC}"
        exit 0
    fi
}

# 运行主函数
main