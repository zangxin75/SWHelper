# 🚀 GitHub 仓库创建和推送指南

本文档提供详细的步骤，指导您如何将 SWHelper 项目推送到 GitHub。

---

## 📋 前置条件

1. ✅ **GitHub 账户** - 如果还没有，请先注册 https://github.com/signup
2. ✅ **Git 已安装** - 检查: `git --version`
3. ✅ **项目代码已提交** - 检查: `git status` (应该没有未提交的更改)

---

## 🎯 方法一：自动化脚本（推荐）

### Windows 用户

```bash
# 在项目根目录运行
setup_github.bat
```

### Linux/Mac 用户

```bash
# 在项目根目录运行
chmod +x setup_github.sh
./setup_github.sh
```

**脚本功能**：
- 自动检测 GitHub CLI 安装状态
- 交互式输入仓库名称和描述
- 自动创建 GitHub 仓库
- 自动推送代码

---

## 🛠️ 方法二：使用 GitHub CLI

### 步骤 1: 安装 GitHub CLI

**Windows:**
```bash
winget install --id GitHub.cli
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install gh
```

**Mac:**
```bash
brew install gh
```

### 步骤 2: 登录 GitHub

```bash
gh auth login
```

按照提示完成认证：
1. 选择 `GitHub.com`
2. 选择 `HTTPS`
3. 选择 `Yes` (登录)
4. 按提示在浏览器中授权

### 步骤 3: 创建仓库并推送

```bash
# 在项目根目录运行
cd D:\sw2026

# 创建公开仓库
gh repo create SWHelper --public --source=. --remote=origin --push

# 或创建私有仓库
gh repo create SWHelper --private --source=. --remote=origin --push
```

---

## 📝 方法三：手动创建（无需 GitHub CLI）

### 步骤 1: 在 GitHub 网站创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `SWHelper`
   - **Description**: `SolidWorks 2026 自动化设计系统`
   - **可见性**: 选择 Public（公开）或 Private（私有）
3. **不要**勾选 "Add a README file"（我们已经有了）
4. 点击 **Create repository**

### 步骤 2: 添加远程仓库并推送

**方法 A: HTTPS（推荐）**

```bash
# 在项目根目录运行
cd D:\sw2026

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/SWHelper.git

# 推送代码
git push -u origin master
```

**方法 B: SSH**

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin git@github.com:YOUR_USERNAME/SWHelper.git

# 推送代码
git push -u origin master
```

---

## 🔑 身份验证

### 使用 Personal Access Token (推荐)

1. **创建 Token**:
   - 访问 https://github.com/settings/tokens
   - 点击 **Generate new token** → **Generate new token (classic)**
   - 设置名称: `SWHelper Push`
   - 选择权限:
     - ✅ `repo` (完整仓库访问权限)
   - 点击 **Generate token**
   - **复制 token**（只显示一次！）

2. **使用 Token 推送**:

```bash
# 推送时会提示输入用户名和密码
# 用户名: YOUR_GITHUB_USERNAME
# 密码: YOUR_PERSONAL_ACCESS_TOKEN

git push -u origin master
```

### 使用 SSH 密钥

**Windows:**
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥
type %USERPROFILE%\.ssh\id_ed25519.pub | clip
```

**Linux/Mac:**
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub
```

**添加到 GitHub**:
1. 访问 https://github.com/settings/keys
2. 点击 **New SSH key**
3. 粘贴公钥内容
4. 点击 **Add SSH key**

---

## ✅ 验证推送成功

### 检查远程仓库

```bash
git remote -v
```

应该显示:
```
origin  https://github.com/YOUR_USERNAME/SWHelper.git (fetch)
origin  https://github.com/YOUR_USERNAME/SWHelper.git (push)
```

### 查看远程分支

```bash
git branch -r
```

应该显示:
```
origin/master
```

### 在浏览器中访问

打开浏览器访问: `https://github.com/YOUR_USERNAME/SWHelper`

您应该看到:
- ✅ README.md 文件（项目首页）
- ✅ 代码目录结构
- ✅ LICENSE 文件
- ✅ 所有提交记录

---

## 📊 推送后的检查清单

- [ ] README.md 显示正常
- [ ] 代码文件都在仓库中
- [ ] LICENSE 文件存在
- [ ] CI/CD 工作流已创建（.github/workflows/）
- [ ] 提交历史完整
- [ ] 仓库描述正确

---

## 🎨 优化仓库设置

### 设置仓库主题

访问: `https://github.com/YOUR_USERNAME/SWHelper/settings`

**Topics (主题标签)**:
```
solidworks, automation, cad, python, csharp, dotnet, com-api, vba, manufacturing, engineering, 3d-modeling
```

**About (描述)**:
```
🎯 基于 Claude Code + Python + C# COM + SolidWorks MCP 的对话式设计自动化系统

实现 95% 自动化率的 SolidWorks 2026 零件设计与建模

✅ CreatePart: 100% 自动化
✅ 对话式设计
✅ 多语言支持 (Python/C#/VBA)
```

### 启用 GitHub Pages (可选)

如果想托管项目文档网站:

1. 访问 `https://github.com/YOUR_USERNAME/SWHelper/settings/pages`
2. Source 选择: `Deploy from a branch`
3. Branch 选择: `master` → `/ (root)`
4. 点击 Save

### 设置仓库星标提示

在 README.md 顶部添加：

```markdown
[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/SWHelper&type=Date)](https://star-history.com/#YOUR_USERNAME/SWHelper&Date)
```

---

## 🔄 后续更新代码

### 日常工作流

```bash
# 1. 修改代码
# 2. 查看状态
git status

# 3. 添加更改
git add .
# 或添加特定文件
git add README.md

# 4. 提交更改
git commit -m "描述您的更改"

# 5. 推送到 GitHub
git push
```

### 创建新分支

```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 做一些更改...
git add .
git commit -m "Add new feature"

# 推送分支到 GitHub
git push -u origin feature/new-feature
```

### 合并分支（Pull Request）

1. 在 GitHub 网站上创建 Pull Request
2. 或者使用 GitHub CLI:
```bash
gh pr create --title "Add new feature" --body "描述您的更改"
```

---

## ❓ 常见问题

### Q1: 推送时报错 "failed to push some refs"

**A:** 远程仓库有新提交，需要先拉取:

```bash
git pull --rebase origin master
git push origin master
```

### Q2: 提示 "Permission denied (publickey)"

**A:** SSH 密钥未配置或未添加到 GitHub:

```bash
# 测试 SSH 连接
ssh -T git@github.com

# 如果失败，重新添加密钥
# 见上文"使用 SSH 密钥"部分
```

### Q3: 推送很慢或超时

**A:** 增加缓冲区大小:

```bash
git config http.postBuffer 524288000
git push origin master
```

### Q4: 如何更新 README.md 后推送？

**A:**
```bash
git add README.md
git commit -m "docs: update README"
git push
```

### Q5: 如何删除远程仓库？

**A:** 在 GitHub 网站上:
1. 访问仓库设置: `https://github.com/YOUR_USERNAME/SWHelper/settings`
2. 滚动到底部
3. 点击 **Delete this repository**
4. 输入仓库名称确认删除

---

## 🎉 完成！

恭喜！您的 SWHelper 项目已成功推送到 GitHub！

**下一步**:
- 分享仓库链接给同事
- 在社交媒体上分享
- 欢迎他人贡献代码
- 定期更新和维护

**仓库地址**: `https://github.com/YOUR_USERNAME/SWHelper`

---

**如有问题，请查看**:
- [GitHub 官方文档](https://docs.github.com/)
- [Git 官方文档](https://git-scm.com/doc)
- [项目 README.md](README.md)
