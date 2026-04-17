# Repository Guidelines

## Project Structure & Module Organization
This is a Strands AI agent project with an orchestrator + sub-agents architecture.
- `src/release_notes_agent/agents/` contains all agent definitions (orchestrator and specialists).
- `src/release_notes_agent/tools/` contains `@tool` decorated functions used by agents.
- `src/release_notes_agent/config/` holds settings (pydantic-settings), AWS client factory, and system prompts.
- `src/release_notes_agent/ui/` contains Streamlit UI components.
- `app.py` is the Streamlit entry point; `main.py` is the CLI entry point.
- `tests/` holds the test suite collected by pytest.
- `scripts/` contains helper scripts called by the Makefile.
- `docs/` stores documentation sources; `mkdocs.yml` configures the site.
- `docker/` contains Dockerfile and docker-compose.yml.

## Build, Test, and Development Commands
Use `uv` for dependency management and to run tools.
- `make install` installs dev dependencies and pre-commit hooks.
- `make sync` synchronizes dependencies.
- `make run` starts the Streamlit UI.
- `make lint` runs Ruff linting.
- `make type-check` runs type annotation checking.
- `make tests` runs `uv run pytest -v`.
- `make build` builds the package.
- `make docker-build` builds the Docker image.
- `uv run python main.py "query"` runs the agent from CLI.

## Key Patterns

### Agent Creation
All agents use a `create_*_agent()` factory function pattern:
- Orchestrator uses `SummarizingConversationManager` for long-running sessions.
- Sub-agents use `SlidingWindowConversationManager` for focused, short-lived tasks.
- All agents share `BedrockModel` configuration from `settings.py`.

### Tool Definition
```python
from strands import tool

@tool
def my_tool(param: str) -> dict:
    """Docstring becomes the tool description for the agent."""
    return {"result": "value"}
```

### Testing Tools
Use `.__wrapped__()` to test the underlying function, bypassing the `@tool` decorator:
```python
result = my_tool.__wrapped__(param="test")
```

## Coding Style & Naming Conventions
- Indentation is 4 spaces, no tabs.
- Use `snake_case` for functions/variables, `PascalCase` for classes.
- Prefer type hints on public APIs.
- Run `make lint` before opening a pull request.

## Testing Guidelines
- Place tests in `tests/` and name files `test_*.py`.
- Use the `conftest.py` fixtures for mocked AWS credentials.
- Run tests with `make tests`.

## Commit & Pull Request Guidelines
- Use Commitizen for conventional commits: `cz commit`.
- Pull requests should include a concise summary, test results, and any doc updates.
