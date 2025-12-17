# GitHub Setup Guide

This guide will help you push the Gusto project to GitHub.

## ✅ Pre-flight Checks

The `.gitignore` file has been created and verified. The following sensitive/large files are being ignored:

- ✅ `backend/venv/` - Python virtual environment
- ✅ `backend/.env` - Environment variables with secrets
- ✅ `frontend/node_modules/` - Node.js dependencies
- ✅ `backend/swaad.db` - Database files
- ✅ All `.env` files
- ✅ All `*.db` files

## 📋 Step-by-Step Setup

### Step 1: Verify .gitignore is Working

```bash
cd /Users/rashandhillon/pa-manual/ouput-data-s3-bucket/s3-knowledge-base/business/projects/anacodic-ai/gusto

# Check that sensitive files are ignored
git status --ignored | grep -E "(venv|\.env|node_modules|\.db)"
# Should show these files as ignored

# Verify what will be committed
git status
# Should NOT show: venv/, .env, node_modules/, *.db
```

### Step 2: Add Files and Create Initial Commit

```bash
# Add .gitignore first (already done)
git add .gitignore

# Add all other files (respects .gitignore)
git add .

# Verify what's staged
git status

# Create initial commit
git commit -m "Initial commit: Gusto multi-agent restaurant recommendation system

- Multi-agent orchestration with Strands framework
- Yelp AI API integration
- Taste vector matching (6D flavor profiles)
- Beer pairing recommendations
- React frontend with Cognito auth
- FastAPI backend with Pinecone vector search
- Collections, Groups, and Friends features
- Restaurant discover feed and details pages"
```

### Step 3: Create GitHub Repository

**Option A: Using GitHub Website**
1. Go to https://github.com/new
2. Repository name: `gusto` (or your preferred name)
3. Description: "Multi-agent restaurant recommendation system with AI taste matching"
4. Choose **Public** or **Private**
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Using GitHub CLI**
```bash
gh repo create gusto --public --description "Multi-agent restaurant recommendation system"
```

### Step 4: Connect and Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gusto.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/gusto.git

# Verify remote
git remote -v

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

## 🔒 Security Checklist

Before pushing, verify these files are **NOT** in your commit:

```bash
# Check for sensitive files
git ls-files | grep -E "\.env$|venv/|node_modules/|\.db$"

# Should return nothing (or only .env.example files)
```

## 📝 Post-Push Steps

1. **Add repository description** on GitHub
2. **Add topics/tags**: `restaurant-recommendation`, `ai`, `multi-agent`, `fastapi`, `react`
3. **Update README.md** if needed with specific setup instructions
4. **Create issues** for known TODOs or future features
5. **Set up GitHub Actions** for CI/CD (optional)

## 🚨 Important Notes

- **Never commit** `.env` files with real API keys
- **Never commit** database files (they can be regenerated)
- **Never commit** `venv/` or `node_modules/` (use requirements.txt and package.json)
- The `.env.example` files are intentionally included as templates

## 🐛 Troubleshooting

### If you see sensitive files in `git status`:

```bash
# Remove from git cache (but keep local file)
git rm --cached backend/.env
git rm --cached backend/swaad.db

# Update .gitignore if needed
# Then commit the removal
git commit -m "Remove sensitive files from git"
```

### If remote already exists:

```bash
# Check current remote
git remote -v

# Update remote URL if needed
git remote set-url origin https://github.com/YOUR_USERNAME/gusto.git
```

## ✅ Verification

After pushing, verify on GitHub:
- ✅ No `.env` files visible
- ✅ No `venv/` or `node_modules/` directories
- ✅ No database files (`.db`)
- ✅ README.md is visible
- ✅ .gitignore is present
- ✅ All source code is present
