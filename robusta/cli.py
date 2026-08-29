from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from robusta.assessment import Evaluator
from robusta.attacks import Attack
from robusta.attacks.fgsm import FGSM  # noqa: F401  (registers into Attack.registry)
from robusta.attacks.pgd import PGD  # noqa: F401  (registers into Attack.registry)
from robusta.attacks.tuap import TUAP  # noqa: F401  (registers into Attack.registry)
from robusta.core import Scanner
from robusta.core.scanner import AttackConfig, AttackResult, ScanResult

_DEFAULT_TOKEN_ENV = "HF_TOKEN"
_DEFAULT_BATCH_SIZE = 16
_DEFAULT_SPLIT = "test"
_DEFAULT_OUTPUT = "results.json"

_TOP_LEVEL_KEYS = {
    "model",
    "dataset",
    "hf_token_env",
    "split",
    "size",
    "streaming",
    "batch_size",
    "output",
    "attack",
}

_OPTIONAL_TOP_LEVEL_KEYS = {
    "hf_token_env": str,
    "split": str,
    "size": int,
    "streaming": bool,
    "batch_size": int,
    "output": str,
}


class ConfigError(ValueError):
    """Raised by the public API for any user-facing failure.

    ``is_config_error`` is ``True`` for problems with the TOML config
    (missing keys, unknown attacks/params, type mismatches, file I/O).
    It is ``False`` for runtime errors encountered while loading the model
    or dataset or writing the report. The CLI uses this to pick between
    exit codes 2 and 1.
    """

    def __init__(self, message: str, *, is_config_error: bool = True) -> None:
        super().__init__(message)
        self.is_config_error = is_config_error


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="robusta",
        description="Adversarial robustness scanner. Reads a TOML config, runs the "
        "configured attacks against the configured model/dataset, and writes a "
        "JSON report. All progress goes to stderr; stdout is left empty.",
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the TOML configuration file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Override the report output path (default: value of `output` in the TOML).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override the scan batch size (default: value of `batch_size` in the TOML).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Override the torch device used by the model (e.g. 'cpu', 'cuda').",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress status messages on stderr (errors are still printed).",
    )
    return parser


def _coerce_toml(value: Any, target: type) -> Any:
    if isinstance(value, bool) and target is not bool:
        if target is int:
            return int(value)
        if target is float:
            return float(value)
        if target is str:
            return "true" if value else "false"
    if isinstance(value, int) and target is float:
        return float(value)
    if target is bool and not isinstance(value, bool):
        if isinstance(value, str):
            lowered = value.lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off"}:
                return False
        raise ConfigError(f"expected bool, got {value!r}")
    if not isinstance(value, target):
        if target in (int, float, str):
            try:
                return target(value)
            except (ValueError, TypeError) as e:
                raise ConfigError(
                    f"expected {target.__name__}, got {value!r}"
                ) from e
        raise ConfigError(
            f"expected {target.__name__}, got {type(value).__name__}"
        )
    return value


def load_config(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as e:
        raise ConfigError(f"cannot read config file {path}: {e}") from e

    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"invalid TOML in {path}: {e}") from e

    if not isinstance(data, dict):
        raise ConfigError(f"{path}: top-level TOML must be a table")

    unknown = set(data) - _TOP_LEVEL_KEYS
    if unknown:
        raise ConfigError(
            f"{path}: unknown top-level keys: {sorted(unknown)}. "
            f"Allowed: {sorted(_TOP_LEVEL_KEYS - {'attack'}) + ['attack.<NAME>']}"
        )

    for required in ("model", "dataset"):
        if required not in data:
            raise ConfigError(f"{path}: missing required key '{required}'")

    for key, target in _OPTIONAL_TOP_LEVEL_KEYS.items():
        if key in data:
            try:
                data[key] = _coerce_toml(data[key], target)
            except ConfigError as e:
                raise ConfigError(
                    f"{path}: key '{key}' must be {target.__name__}, got {data[key]!r}: {e}"
                ) from e

    if "output" not in data:
        raise ConfigError(
            f"{path}: missing required key 'output' "
            "(the CLI is JSON-only; set 'output = \"results.json\"')"
        )

    attacks_raw = data.get("attack")
    if attacks_raw is None:
        raise ConfigError(
            f"{path}: no attacks configured. Add at least one [attack.NAME] table."
        )
    if not isinstance(attacks_raw, dict) or not attacks_raw:
        raise ConfigError(f"{path}: 'attack' must be a non-empty table of [attack.NAME] sections")

    registered = set(Attack.registry)
    for name, table in attacks_raw.items():
        if not isinstance(table, dict):
            raise ConfigError(f"{path}: [attack.{name}] must be a table")
        if name not in registered:
            available = ", ".join(sorted(registered)) or "<none registered>"
            raise ConfigError(
                f"{path}: unknown attack {name!r}. Registered: {available}"
            )
        declared = {p.name for p in Attack.registry[name].attack_parameters()}
        unknown_inner = set(table) - {"enabled"} - declared
        if unknown_inner:
            raise ConfigError(
                f"{path}: [attack.{name}] has unknown keys: {sorted(unknown_inner)}"
            )

    return data


def build_attack_configs(
    attacks_section: dict[str, dict[str, Any]],
    *,
    source: str = "config",
) -> list[AttackConfig]:
    """Build AttackConfig list from a parsed [attack.*] mapping.

    Attacks whose table contains ``enabled = false`` are skipped.
    Unknown attacks or unknown params are rejected.
    """
    out: list[AttackConfig] = []

    for name, table in attacks_section.items():
        enabled = table.get("enabled", True)
        if not enabled:
            continue

        cls = Attack.registry.get(name)
        if cls is None:
            available = ", ".join(sorted(Attack.registry)) or "<none registered>"
            raise ConfigError(
                f"{source}: unknown attack {name!r}. Registered: {available}"
            )

        declared = {p.name: p for p in cls.attack_parameters()}
        params: dict[str, Any] = {}

        for key, value in table.items():
            if key == "enabled":
                continue
            if key not in declared:
                raise ConfigError(
                    f"{source}: [attack.{name}] has unknown parameter {key!r}. "
                    f"Declared: {sorted(declared)}"
                )
            spec = declared[key]
            if spec.optional and value is None:
                continue
            try:
                params[key] = _coerce_toml(value, spec.type)
            except ConfigError as e:
                raise ConfigError(
                    f"{source}: [attack.{name}] parameter {key!r}: {e}"
                ) from e

        missing_required = [
            p.name for p in declared.values() if not p.optional and p.name not in params
        ]
        if missing_required:
            raise ConfigError(
                f"{source}: [attack.{name}] missing required parameters: {missing_required}"
            )

        out.append(AttackConfig(attack=cls, params=params))

    if not out:
        raise ConfigError(f"{source}: no enabled attacks (set 'enabled = true' on at least one)")

    return out


def _resolve_token(env_var: str, *, source: str) -> str:
    token = os.environ.get(env_var)
    if not token:
        raise ConfigError(
            f"{source}: Hugging Face token not found in environment variable {env_var!r}. "
            f"Export it before running robusta.",
            is_config_error=False,
        )
    return token


def _scan_stats(scan: ScanResult, attack: AttackResult) -> dict[str, Any]:
    accuracy = float((scan.pred == scan.y).float().mean())
    adv_accuracy = float((attack.adv_pred == scan.y).float().mean())
    return {
        "clean_accuracy": accuracy,
        "adv_accuracy": adv_accuracy,
        "avg_confidence": float(scan.confidence.mean()),
        "avg_adv_confidence": float(attack.adv_confidence.mean()),
        "attack_time_seconds": float(attack.attack_time_seconds),
        "num_samples": int(len(scan.x)),
    }


def _build_report(
    *,
    config_path: Path,
    config_data: dict[str, Any],
    attack_configs: Sequence[AttackConfig],
    scan: ScanResult,
    evaluation: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    attack_payload: dict[str, dict[str, Any]] = {}
    eval_by_name = {name: evaluation.get(name, {}) for name in evaluation}

    for _attack_cfg, attack_res in zip(attack_configs, scan.results, strict=True):
        name = attack_res.attack_name
        attack_payload[name] = {
            "params": dict(attack_res.attack_params),
            "scan": _scan_stats(scan, attack_res),
            "evaluation": eval_by_name.get(name, {}),
        }

    return {
        "config_path": str(config_path.resolve()),
        "model": config_data["model"],
        "dataset": config_data["dataset"],
        "split": config_data.get("split", _DEFAULT_SPLIT),
        "size": config_data.get("size"),
        "streaming": bool(config_data.get("streaming", False)),
        "batch_size": config_data.get("batch_size", _DEFAULT_BATCH_SIZE),
        "attacks": attack_payload,
    }


def _emit_stderr(message: str, *, quiet: bool) -> None:
    if not quiet:
        print(message, file=sys.stderr, flush=True)


def _run_scan(
    *,
    config_data: dict[str, Any],
    attack_configs: Sequence[AttackConfig],
    batch_size: int,
    device: str | None,
    quiet: bool,
) -> ScanResult:
    token_env = config_data.get("hf_token_env", _DEFAULT_TOKEN_ENV)
    token = _resolve_token(token_env, source="config")

    scanner = Scanner()

    _emit_stderr(f"[robusta] Logging in to Hugging Face (env {token_env!r})...", quiet=quiet)
    if not scanner.set_token(token):
        raise ConfigError(
            "Failed to log in to Hugging Face (invalid token?)",
            is_config_error=False,
        )

    _emit_stderr(
        f"[robusta] Loading model {config_data['model']!r}...",
        quiet=quiet,
    )
    if not scanner.set_model(
        model_id=config_data["model"],
        device=device,
    ):
        raise ConfigError(
            f"Failed to load model {config_data['model']!r}",
            is_config_error=False,
        )

    streaming = bool(config_data.get("streaming", False))
    size = config_data.get("size")

    _emit_stderr(
        f"[robusta] Loading dataset {config_data['dataset']!r} "
        f"(split={config_data.get('split', _DEFAULT_SPLIT)}, "
        f"size={size}, streaming={streaming})...",
        quiet=quiet,
    )
    if not scanner.set_dataset(
        dataset_id=config_data["dataset"],
        split=config_data.get("split", _DEFAULT_SPLIT),
        size=size,
        streaming=streaming,
    ):
        raise ConfigError(
            f"Failed to load dataset {config_data['dataset']!r} "
            f"(check the dataset id, split, size, and streaming settings)",
            is_config_error=False,
        )

    scanner.set_attacks(attack_configs)

    total_attacks = len(attack_configs)
    for index, cfg in enumerate(attack_configs, start=1):
        _emit_stderr(
            f"[robusta] Running attack {index}/{total_attacks}: {cfg.attack.name()}...",
            quiet=quiet,
        )

    return scanner.run(batch_size=batch_size)


def run(
    config_path: str | os.PathLike[str],
    *,
    output: str | os.PathLike[str] | None = None,
    batch_size: int | None = None,
    device: str | None = None,
    quiet: bool = False,
) -> dict[str, Any]:
    """Load a TOML config, run the scan, evaluate, and return the report.

    Parameters
    ----------
    config_path
        Path to the TOML configuration file.
    output
        Path to write the JSON report. If ``None`` (default), the path is
        taken from the ``output`` key in the TOML.
    batch_size
        Override the scan batch size.
    device
        Override the torch device for the model.
    quiet
        Suppress progress messages on stderr.

    Returns
    -------
    dict
        The full report dict (same shape as the JSON file written by the CLI).

    Raises
    ------
    ConfigError
        On configuration errors (missing/invalid keys, unknown attacks or
        parameters) or runtime errors (HF login, model/dataset load failure,
        file write failure).
    """
    config_file = Path(config_path)
    config_data = load_config(config_file)
    attack_configs = build_attack_configs(
        config_data["attack"], source=str(config_file)
    )

    effective_batch_size: int = (
        batch_size if batch_size is not None
        else int(config_data.get("batch_size", _DEFAULT_BATCH_SIZE))
    )

    output_path: Path | None
    if output is None:
        output_path = Path(config_data["output"])
    else:
        output_path = Path(output)

    scan = _run_scan(
        config_data=config_data,
        attack_configs=attack_configs,
        batch_size=effective_batch_size,
        device=device,
        quiet=quiet,
    )

    _emit_stderr("[robusta] Evaluating results...", quiet=quiet)
    evaluation = Evaluator().evaluate(scan)

    report = _build_report(
        config_path=config_file,
        config_data=config_data,
        attack_configs=attack_configs,
        scan=scan,
        evaluation=evaluation,
    )

    if output_path is not None:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(report, indent=2, default=_json_default))
        except OSError as e:
            raise ConfigError(
                f"cannot write report to {output_path}: {e}",
                is_config_error=False,
            ) from e
        _emit_stderr(f"[robusta] Wrote report to {output_path}", quiet=quiet)

    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        run(
            args.config,
            output=args.output,
            batch_size=args.batch_size,
            device=args.device,
            quiet=args.quiet,
        )
    except ConfigError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2 if e.is_config_error else 1
    else:
        return 0


def _json_default(obj: Any) -> Any:
    import torch

    if isinstance(obj, torch.Tensor):
        return obj.detach().cpu().tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


if __name__ == "__main__":
    raise SystemExit(main())
