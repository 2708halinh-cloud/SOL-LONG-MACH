"""Static safety checks; runtime integration tests require configured upstreams."""
from pathlib import Path

SOURCE = Path(__file__).parents[1] / "server.py"


def test_no_embedded_tokens_or_private_keys():
    text = SOURCE.read_text(encoding="utf-8")
    assert "-----BEGIN PRIVATE KEY-----" not in text
    assert "ghp_" not in text
    assert "sk-proj-" not in text


def test_only_read_only_upstream_tools_are_declared():
    text = SOURCE.read_text(encoding="utf-8")
    assert "def github_repository_readme" in text
    assert "def chroma_heartbeat" in text
    assert "def azure_devops_list_projects" in text
    assert "def google_drive_list_files" in text
    assert "def local_bridge_status" in text
    assert "def android_bridge_status" in text
    assert "def gateway_status" in text
    assert "def execute_shell" not in text
    assert "def run_adb" not in text


def test_bearer_guard_and_health_route_exist():
    text = SOURCE.read_text(encoding="utf-8")
    assert "secrets.compare_digest" in text
    assert 'app.add_route("/healthz"' in text
    assert '"/mcp"' not in text or "streamable_http_app" in text
