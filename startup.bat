@echo off
echo === Setting up release-notes-agent ===

REM Step 1: Initialize git repository
if not exist ".git" (
    echo Initializing git repository...
    git init --initial-branch=main
) else (
    echo Git repository already initialized.
)

REM Step 2: Copy .env.example to .env
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please fill in your AWS credentials in .env
) else (
    echo .env already exists, skipping.
)

REM Step 3: Install dependencies and pre-commit hooks
echo Installing dependencies...
uv sync
uv run pre-commit install

REM Step 4: Stage and commit files
echo Staging and committing files...
git add .
git commit -m "feat: first commit"
if errorlevel 1 echo Nothing to commit.

REM Step 5: Add remote and push
set REMOTE_URL=https://github.com/bravetux/release-notes-agent.git
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding remote origin...
    git remote add origin %REMOTE_URL%
) else (
    echo Remote origin already set.
)
echo Pushing to remote...
git push --set-upstream origin main
if errorlevel 1 echo Push failed. You may need to create the repository on GitHub first.

REM Step 6: Done
echo.
echo === Setup complete! ===
echo To start the Streamlit UI, run: make run
echo Or directly: uv run streamlit run app.py
