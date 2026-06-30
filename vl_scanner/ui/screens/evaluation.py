from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label


class EvaluationScreen(Screen):
    """Screen that displays the evaluation results in a table."""

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
    ]

    def __init__(self, result: dict[str, Any]) -> None:
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

    def on_mount(self) -> None:
        table = self.query_one("#eval-table", DataTable)
        metrics = self.result["extent_of_damage"]["metrics_detail"]
        effort = self.result["attackers_effort"]
        num_attacks = effort.get("attack_steps", 1) or 1

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
            ("Attack Time (s)", 14),
            ("CPU (%)", 8),
        ]
        for name, width in columns:
            table.add_column(name, width=width)

        for i in range(num_attacks):
            row = [
                f"Attack {i + 1}",
                self.result["etsi_risk_level"],
                f"{self.result['extent_of_damage']['composite_score']:.2f}",
                f"{metrics['inverted_accuracy']:.2f}",
                f"{metrics['inverted_macro_precision']:.2f}",
                f"{metrics['inverted_macro_recall']:.2f}",
                f"{metrics['inverted_macro_f1']:.2f}",
                f"{metrics['average_confidence_drop']:.2f}",
                str(effort["attack_steps"]),
                f"{effort['attack_time_seconds']:.2f}",
                f"{effort['computational_resources']['cpu_percent']:.2f}",
            ]
            table.add_row(*row)
