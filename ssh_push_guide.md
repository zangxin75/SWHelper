# 🔐 SSH 推送设置指南 - zangxin75

## SSH 公钥

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEnwQmhhryzPNy3CgBK5pdEQyydSP5kjvPhivevHPIzq zangxin75@github
```

## ⚡ 快速设置（2分钟）

### 步骤 1: 添加 SSH 密钥到 GitHub（1分钟）

1. **打开浏览器访问**:
   ```
   https://github.com/settings/ssh/new
   ```

2. **填写信息**:
   - Title: `SWHelper-PC` 或任意名称
   - Key: 复制上面的公钥（整行）
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEnwQmhhryzPNy3CgBK5pdEQyydSP5kjvPhivevHPIzq zangxin75@github
   ```

3. 点击 **Add SSH key**

### 步骤 2: 测试 SSH 连接

在 Git Bash 或 PowerShell 中运行:
```bash
ssh -T git@github.com
```

首次连接会提示：
```
Are you sure you want to continue connecting (yes/no)?
```
输入 `yes` 并回车。

成功会显示：
```
Hi zangxin75! You've successfully authenticated...
```

### 步骤 3: 推送代码

```bash
cd D:\sw2026
git remote set-url origin git@github.com:zangxin75/SWHelper.git
git push -u origin master
```

## ✅ 完成！

推送成功后访问:
```
https://github.com/zangxin75/SWHelper
```

---

## 📝 一键脚本（推荐）

我已经为您准备了自动化脚本：

**双击运行**: `D:\sw2026\ssh_push.bat`

脚本会自动：
1. 配置远程仓库为 SSH
2. 测试 SSH 连接
3. 推送代码到 GitHub
4. 打开浏览器查看结果

---

## 🔑 SSH 优势

- ✅ 无需每次输入 Token
- ✅ 更安全（加密密钥）
- ✅ 更方便（一次配置，永久使用）
- ✅ GitHub 官方推荐方法

---

准备好了吗？开始设置！🚀
