# release-notes-agent

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A Strands AI agent project

Built with [Strands Agents SDK](https://github.com/strands-agents/sdk-python) + AWS Bedrock.

## Architecture

**Orchestrator + specialist sub-agents** pattern:

- **Orchestrator** (`src/release_notes_agent/agents/orchestrator.py`) — routes user queries to specialist sub-agents, aggregates results
- **Example Agent** (`src/release_notes_agent/agents/example_agent.py`) — starter sub-agent demonstrating the factory pattern
- **Tools** (`src/release_notes_agent/tools/`) — `@tool` decorated functions available to agents
- **Config** (`src/release_notes_agent/config/`) — pydantic-settings, AWS client, system prompts
- **UI** (`app.py`) — Streamlit chat interface

## Quickstart

### 1. Install `uv`

This project uses [uv](https://github.com/astral-sh/uv) as package manager.

Linux/MacOS (bash):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (powershell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone repository

```bash
git clone https://github.com/bravetux/release-notes-agent
cd release-notes-agent
```

### 3. Run initial setup

```bash
make install
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your AWS credentials and Bedrock model ID
```

### 5. Run the application

```bash
# Streamlit UI (Generate tab + Chat tab)
make run

# CLI — generate release notes
uv run python main.py generate \
  --srs tests/fixtures/srs_small.md \
  --sample tests/fixtures/sample_release_notes.md \
  --product "Demo" --version 1.2.0 --date 2026-04-17 \
  --audience both --format docx --out .releases/demo.docx

# CLI — interactive chat
uv run python main.py chat
```

**PDF export note:** WeasyPrint requires GTK on Windows
([setup guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)).
The Docker image installs it via `apt`. MD / HTML / DOCX work without GTK.

## Makefile commands

- `install` — Installs dependencies and pre-commit hooks.
- `sync` — Synchronizes dependencies via `scripts/sync.sh`.
- `run` — Starts the Streamlit UI.
- `lint` — Runs Ruff linting and format checking.
- `tests` — Runs pytest with coverage.
- `type-check` — Runs type checking with Ruff annotation rules.
- `build` — Builds the package.
- `init-docs` — Initializes the documentation branch.
- `github-pages` — Publishes documentation to GitHub Pages.
- `github-tag` — Creates a version tag.
- `print-version` — Prints the current version.
- `docker-build` — Builds the Docker image.
- `docker-up` — Starts the Docker container.

## Adding a new sub-agent

1. Create a new file in `src/release_notes_agent/agents/` with a `create_*_agent()` factory.
2. Create tools in `src/release_notes_agent/tools/`.
3. Import and register the agent/tools in `orchestrator.py`.

## Documentation

```bash
make init-docs   # first time only
make github-pages
```

After publishing, docs are at `https://bravetux.github.io/release-notes-agent/`.
