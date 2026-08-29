from __future__ import annotations

from pathlib import Path

import pytest

from robusta.cli import ConfigError, build_attack_configs, load_config


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(body)
    return path


def test_minimal_valid_config_parses(tmp_path):
    path = _write(
        tmp_path,
        """
        model   = "x/y"
        dataset = "a/b"
        output  = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    data = load_config(path)
    assert data["model"] == "x/y"
    assert data["dataset"] == "a/b"
    assert data["output"] == "out.json"


def test_missing_required_keys_raises(tmp_path):
    path = _write(
        tmp_path,
        """
        output = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError, match="missing required key 'model'"):
        load_config(path)

    path = _write(
        tmp_path,
        """
        model = "x/y"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError, match="missing required key 'dataset'"):
        load_config(path)

    path = _write(
        tmp_path,
        """
        model   = "x/y"
        dataset = "a/b"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError, match="missing required key 'output'"):
        load_config(path)


def test_unknown_top_level_key_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"
        not_a_real_key = 1

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError, match="unknown top-level keys"):
        load_config(path)


def test_top_level_types_coerced(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"
        size = 100
        streaming = true
        batch_size = 8
        split = "train"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    data = load_config(path)
    assert data["size"] == 100
    assert data["streaming"] is True
    assert data["batch_size"] == 8
    assert data["split"] == "train"


def test_top_level_wrong_type_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"
        size = "not-an-int"

        [attack.FGSM]
        epsilon = 0.03
        """,
    )
    with pytest.raises(ConfigError, match="'size' must be int"):
        load_config(path)


def test_build_attack_skips_disabled(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.FGSM]
        enabled = false
        epsilon = 0.03
        """,
    )
    data = load_config(path)
    with pytest.raises(ConfigError, match="no enabled attacks"):
        build_attack_configs(data["attack"], source=str(path))

    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.FGSM]
        enabled = true
        epsilon = 0.05
        """,
    )
    data = load_config(path)
    configs = build_attack_configs(data["attack"], source=str(path))
    assert len(configs) == 1
    assert configs[0].attack.name() == "FGSM"
    assert configs[0].params == {"epsilon": 0.05}


def test_build_attack_rejects_unknown_attack(tmp_path):
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
    with pytest.raises(ConfigError, match="unknown attack 'NOPE'"):
        load_config(path)


def test_build_attack_rejects_unknown_param(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.FGSM]
        epsilon = 0.03
        not_a_real_param = 1
        """,
    )
    with pytest.raises(ConfigError, match="unknown keys"):
        load_config(path)


def test_build_attack_coerces_param_types(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.PGD]
        epsilon  = 0.1
        alpha    = "0.02"
        num_iter = "40"
        """,
    )
    data = load_config(path)
    configs = build_attack_configs(data["attack"], source=str(path))
    assert configs[0].params == {"epsilon": 0.1, "alpha": 0.02, "num_iter": 40}


def test_build_attack_wrong_param_type_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        model = "x/y"
        dataset = "a/b"
        output = "out.json"

        [attack.PGD]
        epsilon  = "not-a-float"
        alpha    = 0.01
        num_iter = 40
        """,
    )
    data = load_config(path)
    with pytest.raises(ConfigError, match="expected float"):
        build_attack_configs(data["attack"], source=str(path))


def test_invalid_toml_rejected(tmp_path):
    path = _write(tmp_path, "this is = = not valid toml =")
    with pytest.raises(ConfigError, match="invalid TOML"):
        load_config(path)


def test_missing_config_file(tmp_path):
    with pytest.raises(ConfigError, match="cannot read config file"):
        load_config(tmp_path / "does-not-exist.toml")
