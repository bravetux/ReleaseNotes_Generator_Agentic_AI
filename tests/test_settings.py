"""Tests for settings module."""

from release_notes_agent.config.settings import Settings


class TestSettings:
    def test_default_region(self):
        s = Settings(
            AWS_ACCESS_KEY_ID="test",
            AWS_SECRET_ACCESS_KEY="test",
        )
        assert s.aws_region == "us-east-1"

    def test_default_model(self):
        s = Settings(
            AWS_ACCESS_KEY_ID="test",
            AWS_SECRET_ACCESS_KEY="test",
        )
        assert "claude" in s.bedrock_model_id

    def test_default_temperature(self):
        s = Settings(
            AWS_ACCESS_KEY_ID="test",
            AWS_SECRET_ACCESS_KEY="test",
        )
        assert s.agent_temperature == 0.1

    def test_override_from_env(self, monkeypatch):
        monkeypatch.setenv("AGENT_TEMPERATURE", "0.5")
        s = Settings(
            AWS_ACCESS_KEY_ID="test",
            AWS_SECRET_ACCESS_KEY="test",
        )
        assert s.agent_temperature == 0.5

    def test_session_defaults(self):
        s = Settings(
            AWS_ACCESS_KEY_ID="test",
            AWS_SECRET_ACCESS_KEY="test",
        )
        assert s.session_backend == "file"
        assert s.session_dir == ".sessions"
