#!/usr/bin/env bash
set -euo pipefail

echo "=== Setting up release-notes-agent ==="

# Step 1: Initialize git repository
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init --initial-branch=main
else
    echo "Git repository already initialized."
fi

# Step 2: Copy .env.example to .env
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please fill in your AWS credentials in .env"
else
    echo ".env already exists, skipping."
fi

# Step 3: Install dependencies and pre-commit hooks
echo "Installing dependencies..."
chmod +x ./scripts/*.sh
uv sync
uv run pre-commit install

# Step 4: Stage and commit files
echo "Staging and committing files..."
git add .
git commit -m "feat: first commit" || echo "Nothing to commit."

# Step 5: Add remote and push
REMOTE_URL="https://github.com/bravetux/release-notes-agent.git"
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Adding remote origin..."
    git remote add origin "$REMOTE_URL"
else
    echo "Remote origin already set."
fi
echo "Pushing to remote..."
git push --set-upstream origin main || echo "Push failed. You may need to create the repository on GitHub first."

# Step 6: Run the Streamlit UI
echo ""
echo "=== Setup complete! ==="
echo "To start the Streamlit UI, run: make run"
echo "Or directly: uv run streamlit run app.py"
