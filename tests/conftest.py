"""Shared test fixtures for release-notes-agent."""

import tempfile

import pytest


@pytest.fixture(autouse=True)
def _env_defaults(monkeypatch):
    """Ensure tests never hit real AWS by setting dummy credentials."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0")


@pytest.fixture
def temp_session_dir():
    """Provide a temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
