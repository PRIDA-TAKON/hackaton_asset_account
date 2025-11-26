@echo off
echo ==========================================
echo    Hackathon Asset Account - Git Deploy
echo ==========================================

echo 1. Initializing Git...
git init

echo 2. Setting up 'main' branch...
git checkout -B main

echo 3. Adding files to staging...
git add .

echo 4. Committing changes...
git commit -m "Prepare for Hugging Face deployment"

echo 5. Configuring Remote URL...
:: Remove existing origin if it exists to avoid errors
git remote remove origin 2>NUL
git remote add origin https://github.com/PRIDA-TAKON/hackaton_asset_account

echo 6. Pushing to GitHub...
echo    (This will FORCE push to 'main', overwriting history on remote 'main')
git push -u origin main --force

echo ==========================================
echo    Deployment Complete!
echo ==========================================
echo.
echo To delete other branches on GitHub, you can go to:
echo https://github.com/PRIDA-TAKON/hackaton_asset_account/branches
echo and delete them manually, or run: git push origin --delete <branch_name>
echo.
pause
