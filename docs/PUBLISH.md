# GitHub 发布指南

## 方法一：通过 GitHub CLI（推荐）

### 1. 安装 GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y

# Windows
winget install --id GitHub.cli
```

### 2. 登录 GitHub

```bash
gh auth login
# 按提示选择 HTTPS / Y / 浏览器登录
```

### 3. 创建仓库并推送

```bash
cd /root/.openclaw/workspace/sprint-agent-v2

# 创建公开仓库
gh repo create sprint-agent --public --source=. --remote=origin --push

# 或创建私有仓库
gh repo create sprint-agent --private --source=. --remote=origin --push
```

### 4. 验证

```bash
gh repo view sprint-agent --web
```

## 方法二：手动操作

### 1. 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名：`sprint-agent`
3. 选择 Public 或 Private
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 2. 推送代码

```bash
cd /root/.openclaw/workspace/sprint-agent-v2

# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/sprint-agent.git

# 推送
git push -u origin main
```

### 3. 验证

访问 `https://github.com/YOUR_USERNAME/sprint-agent`

## 方法三：通过 OpenClaw 自动发布

如果你有 GitHub Personal Access Token：

```bash
# 设置 token
export GITHUB_TOKEN=your_token_here

# 使用 gh CLI 创建并推送
cd /root/.openclaw/workspace/sprint-agent-v2
gh repo create sprint-agent --public --source=. --remote=origin --push
```

## 发布后的设置

### 启用 GitHub Pages（可选，用于在线看板演示）

```bash
gh repo edit --enable-pages --pages-branch main --pages-source /web
```

### 创建 Release

```bash
# 创建标签
git tag -a v1.0.0 -m "Sprint Agent v1.0.0 - Initial Release"
git push origin v1.0.0

# 创建 Release
gh release create v1.0.0 --title "Sprint Agent v1.0.0" \
  --notes "首次发布，包含完整的 Sprint 管理功能：
- Trello 风格看板
- Planning / Standup / Retro / Assessment 全流程
- Interview/Grill 自动追问
- Docker 一键部署
- REST API 接口"
```

## 常见问题

### Q: 提示没有权限

确保你的 GitHub 账号有创建仓库的权限，且 token 包含 `repo` 权限。

### Q: 推送失败 "repository not found"

检查远程地址是否正确：
```bash
git remote -v
# 如果不正确，重新设置
git remote set-url origin https://github.com/YOUR_USERNAME/sprint-agent.git
```

### Q: 需要输入密码

使用 Personal Access Token 代替密码：
1. 访问 https://github.com/settings/tokens
2. 生成 token（勾选 repo 权限）
3. 用 token 作为密码

### Q: 已有同名仓库

先删除旧仓库或换一个名字：
```bash
gh repo create sprint-agent-v2 --public --source=. --remote=origin --push
```

## 项目地址模板

发布后项目地址：
```
https://github.com/YOUR_USERNAME/sprint-agent
```

README 中的链接需要更新为实际地址（批量替换 `yourusername`）。
