from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, TabbedContent, TabPane
from vl_scanner.core.scanner import Scanner
from vl_scanner.ui.widgets.attack_selector import AttackSelector
from vl_scanner.ui.widgets.model_selector_tab import ModelSelector


class ScanConfigScreen(Screen):
    DEFAULT_CSS = """
    ScanConfigScreen TabbedContent {
        height: 100%;
    }
    ScanConfigScreen ContentSwitcher {
        height: 1fr;
    }
    ScanConfigScreen TabPane {
        height: 100%;
        padding: 0;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.scanner = Scanner()

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Model/Dataset", id="model_dataset_tab"):
                yield ModelSelector()
            with TabPane("Attacks", id="attacks_tab"):
                yield AttackSelector()
            with TabPane("Parameters", id="parameters_tab"):
                pass

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        try:
            model_input = self.query_one("#model_id", Input)
            dataset_input = self.query_one("#dataset_id", Input)
        except Exception:
            return

        model_val = model_input.value.strip()
        if model_val:
            self.scanner.set_model(model_id=model_val)

        dataset_val = dataset_input.value.strip()
        if dataset_val:
            self.scanner.set_dataset(dataset_id=dataset_val)


