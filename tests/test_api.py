from __future__ import annotations

from pathlib import Path

import pytest

import robusta
from robusta import ConfigError, run


def test_public_api_exports():
    assert robusta.run is run
    assert robusta.ConfigError is ConfigError
    assert isinstance(robusta.__version__, str)
    assert robusta.__version__


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(body)
    return path


def test_run_propagates_config_errors(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.NOPE]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError) as info:
        run(path)
    assert info.value.is_config_error is True
    assert "unknown attack 'NOPE'" in str(info.value)


def test_run_raises_missing_required(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        output = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError) as info:
        run(path)
    assert info.value.is_config_error is True
    assert "missing required key 'dataset'" in str(info.value)


def test_run_raises_missing_file(tmp_path):
    with pytest.raises(ConfigError) as info:
        run(tmp_path / "missing.toml")
    assert info.value.is_config_error is True


def test_run_accepts_string_path(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    # Should not raise before the HF-dependent stage.
    with pytest.raises(ConfigError) as info:
        run(str(path))
    # The failure here is HF login (no HF_TOKEN in this test env), which is a runtime
    # (non-config) error.
    assert info.value.is_config_error is False


def test_run_propagates_hf_login_failure_as_runtime_error(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError) as info:
        run(path, quiet=True)
    assert info.value.is_config_error is False
    assert "HF_TOKEN" in str(info.value)
