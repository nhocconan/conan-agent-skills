import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refsync


def _settings(tmp_path, cmd):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"model": "x", "hooks": {"Stop": [{"hooks": [{"type": "command", "command": cmd, "timeout": 5}]}]}}))
    return p


def test_removes_hook_whose_script_is_missing(tmp_path):
    p = _settings(tmp_path, str(tmp_path / "nope" / "timeline-stop-hook"))
    removed = refsync.prune_dead_hooks(p)
    assert len(removed) == 1
    data = json.loads(p.read_text())
    assert "hooks" not in data and data["model"] == "x"
    assert (tmp_path / "settings.json.bak-dead-hooks").exists()


def test_keeps_hook_whose_script_exists(tmp_path):
    script = tmp_path / "hook"; script.write_text("#!/bin/sh\nexit 0\n")
    p = _settings(tmp_path, str(script))
    assert refsync.prune_dead_hooks(p) == []
    assert "hooks" in json.loads(p.read_text())


def test_dry_run_does_not_write(tmp_path):
    p = _settings(tmp_path, str(tmp_path / "missing"))
    before = p.read_text()
    assert refsync.prune_dead_hooks(p, dry_run=True)
    assert p.read_text() == before
