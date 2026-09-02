# GitHub Setup Instructions

## Prerequisites

1. **Install Git**: Download from https://git-scm.com/download/win
2. **Create GitHub Account**: https://github.com/signup
3. **Configure Git** (after installation):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## Step-by-Step GitHub Setup

### 1. Initialize Git Repository
Open Command Prompt or PowerShell in the project directory:
```bash
cd "C:\Users\noah.jallow\OneDrive - vzw Scholen Molenland\Documenten\SystemInfoTool"
git init
```

### 2. Add All Files
```bash
git add .
```

### 3. Create Initial Commit
```bash
git commit -m "Initial commit: Cross-platform System Info Tool with enhanced hardware detection"
```

### 4. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `SystemInfoTool`
3. Description: `Cross-platform system information tool with enhanced hardware detection`
4. Make it **Public** or **Private** (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 5. Connect Local Repository to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/SystemInfoTool.git
```
Replace `YOUR_USERNAME` with your actual GitHub username.

### 6. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## Authentication Options

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. When prompted for password during `git push`, use the token as password

### Option 2: SSH Key Setup
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your.email@example.com"`
2. Add SSH key to GitHub account
3. Use SSH URL: `git@github.com:YOUR_USERNAME/SystemInfoTool.git`

## Verification

After successful push, verify your repository at:
https://github.com/YOUR_USERNAME/SystemInfoTool

## Troubleshooting

### "fatal: not a git repository"
- Make sure you're in the correct directory
- Run `git init` first

### "Authentication failed"
- Use Personal Access Token instead of password
- Check your token has correct permissions

### "remote origin already exists"
- Remove existing remote: `git remote remove origin`
- Add new remote: `git remote add origin https://github.com/YOUR_USERNAME/SystemInfoTool.git`

### Push rejected
- Try: `git pull origin main --allow-unrelated-histories`
- Then: `git push -u origin main`

## Next Steps

After successful push:
1. Add repository description on GitHub
2. Add topics/tags (e.g., `system-info`, `hardware-detection`, `python`, `cross-platform`)
3. Enable GitHub Actions if you want CI/CD
4. Add collaborators if working with a team
5. Create releases for distribution builds