#!/bin/bash
# GitHub 仓库创建和推送脚本

echo "================================"
echo "SWHelper GitHub 仓库设置向导"
echo "================================"
echo ""

# 检查是否已登录 GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安装"
    echo ""
    echo "请安装 GitHub CLI:"
    echo "  Windows: winget install --id GitHub.cli"
    echo "  或下载: https://cli.github.com/"
    echo ""
    echo "或者手动创建仓库:"
    echo "  1. 访问 https://github.com/new"
    echo "  2. 创建新仓库 'SWHelper'"
    echo "  3. 运行: git remote add origin https://github.com/YOUR_USERNAME/SWHelper.git"
    echo "  4. 运行: git push -u origin master"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录 GitHub"
    echo "请先登录:"
    echo "  gh auth login"
    exit 1
fi

echo "✅ GitHub CLI 已就绪"
echo ""

# 获取仓库信息
read -p "仓库名称 [SWHelper]: " REPO_NAME
REPO_NAME=${REPO_NAME:-SWHelper}

read -p "仓库描述 [SolidWorks 2026 自动化设计系统]: " REPO_DESC
REPO_DESC=${REPO_DESC:-SolidWorks 2026 自动化设计系统}

read -p "是否为私有仓库? (y/N): " IS_PRIVATE
if [[ $IS_PRIVATE =~ ^[Yy]$ ]]; then
    PRIVATE_FLAG="--private"
else
    PRIVATE_FLAG="--public"
fi

echo ""
echo "================================"
echo "准备创建 GitHub 仓库"
echo "================================"
echo "仓库名称: $REPO_NAME"
echo "描述: $REPO_DESC"
echo "可见性: $([ "$PRIVATE_FLAG" = "--private" ] && echo "私有" || echo "公开")"
echo ""

read -p "确认创建? (Y/n): " CONFIRM
if [[ $CONFIRM =~ ^[Nn]$ ]]; then
    echo "已取消"
    exit 0
fi

# 创建仓库
echo ""
echo "正在创建 GitHub 仓库..."
gh repo create "$REPO_NAME" \
    --description "$REPO_DESC" \
    $PRIVATE_FLAG \
    --source=. \
    --remote=origin \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ 仓库创建成功！"
    echo "================================"
    echo ""
    gh repo view "$REPO_NAME" --web
else
    echo ""
    echo "❌ 创建失败，请手动创建"
    echo ""
    echo "手动步骤:"
    echo "  1. 访问 https://github.com/new"
    echo "  2. 创建仓库 '$REPO_NAME'"
    echo "  3. 运行以下命令:"
    echo "     git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "     git push -u origin master"
fi
