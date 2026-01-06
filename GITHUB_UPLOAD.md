# How to Upload to GitHub

## Step 1: Initialize Git Repository (if not already done)

```bash
git init
```

## Step 2: Add All Files

```bash
git add .
```

This will add all files except those in `.gitignore` (like your API key, output files, etc.)

## Step 3: Make Your First Commit

```bash
git commit -m "Initial commit: RPS simulation with ECS, resources, travel, and XAI API integration"
```

## Step 4: Create a GitHub Repository

1. Go to https://github.com
2. Click the "+" icon in the top right
3. Select "New repository"
4. Name it (e.g., "rps-simulation" or "ttrpg-simulation")
5. **DO NOT** initialize with README, .gitignore, or license (you already have these)
6. Click "Create repository"

## Step 5: Connect and Push

GitHub will show you commands. Use these:

```bash
# Add the remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push your code
git push -u origin main
```

## Alternative: Using GitHub CLI (if you have it installed)

```bash
gh repo create REPO_NAME --public --source=. --remote=origin --push
```

## What Gets Uploaded

✅ **Will be uploaded:**
- All Python files (.py)
- README.md
- requirements.txt
- .gitignore
- SETUP.md
- XAI_SETUP.md
- xai_evolution.py.example (template, if it exists)

❌ **Will NOT be uploaded** (protected by .gitignore):
- Your API key in xai_evolution.py (if you added it locally)
- Output files (`output_file/` directory, `*.txt` reports, `*.json` state files)
- `__pycache__` folders
- `.env` files

## After Uploading

1. Go to your GitHub repository page
2. Verify all files are there
3. Check that `xai_evolution.py` does NOT contain your API key
4. Share the repo link with others!

