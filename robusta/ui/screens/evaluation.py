import json
from datetime import datetime
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label


def _format(value: float | int | None, fmt: str = ".2f") -> str:
    return "N/A" if value is None else format(float(value), fmt)


def _etsi_risk_level(composite_score: float | None) -> str:
    if composite_score is None:
        return "N/A"
    if composite_score >= 3.0:
        return "Critical"
    if composite_score >= 2.0:
        return "Major"
    if composite_score >= 1.0:
        return "Moderate"
    return "Minor"


class EvaluationScreen(Screen):
    """Screen that displays the evaluation results in a table.

    Expects the dict returned by :class:`robusta.assessment.evaluator.Evaluator`:
    a mapping of ``attack_name`` -> per-attack result containing
    ``extent_of_damage`` (with ``composite_score`` and ``metrics_detail``) and
    ``attackers_effort`` (with ``attack_steps`` and ``attack_time_seconds``).
    """

    DEFAULT_CSS = """
    EvaluationScreen {
        align: center middle;
    }

    #eval-container {
        width: 95%;
        height: auto;
        max-height: 90%;
        padding: 1 2;
        border: round $accent;
    }

    #eval-title {
        text-align: center;
        margin-bottom: 1;
        text-style: bold;
        width: 100%;
    }

    #eval-table {
        width: 100%;
        height: auto;
    }
    """

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("r", "restart", "Restart"),
        ("e", "export", "Export"),
    ]

    def __init__(self, result: dict[str, dict[str, Any]]) -> None:
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="eval-container"):
            yield Label("Evaluation Results", id="eval-title")
            yield DataTable(id="eval-table")
        yield Footer()

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_restart(self) -> None:
        self.app.switch_screen("ScanConfigScreen")

    def action_export(self) -> None:
        export_dir = Path("export")
        export_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = export_dir / f"{timestamp}.json"
        output_path.write_text(json.dumps(self.result, indent=2, default=str))
        self.notify(f"Exported to {output_path}", title="Export")

    def on_mount(self) -> None:
        table = self.query_one("#eval-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        columns: list[tuple[str, int]] = [
            ("Attack", 12),
            ("ETSI Risk", 11),
            ("Composite", 10),
            ("Inv. Accuracy", 12),
            ("Inv. Macro Precision", 18),
            ("Inv. Macro Recall", 18),
            ("Inv. Macro F1", 14),
            ("Avg Conf Drop", 14),
            ("Attack Steps", 12),
            ("Attack Time (s)", 15),
        ]
        for name, width in columns:
            table.add_column(name, width=width)

        for attack_name, attack_result in self.result.items():
            damage = attack_result.get("extent_of_damage", {}) or {}
            metrics = damage.get("metrics_detail", {}) or {}
            effort = attack_result.get("attackers_effort", {}) or {}
            composite = damage.get("composite_score")

            display_name = (attack_result.get("attack_art") or attack_name).upper()

            table.add_row(
                display_name,
                _etsi_risk_level(composite),
                _format(composite),
                _format(metrics.get("inverted_accuracy")),
                _format(metrics.get("inverted_macro_precision")),
                _format(metrics.get("inverted_macro_recall")),
                _format(metrics.get("inverted_macro_f1")),
                _format(metrics.get("average_confidence_drop")),
                str(effort.get("attack_steps", "N/A")),
                _format(effort.get("attack_time_seconds")),
            )
