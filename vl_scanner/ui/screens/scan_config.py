from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane

from vl_scanner.core.scanner import Scanner
from vl_scanner.ui.widgets.attack_selector import AttackSelector
from vl_scanner.ui.widgets.launch_tab import LaunchTab
from vl_scanner.ui.widgets.model_selector_tab import ModelSelector
from vl_scanner.ui.widgets.parameter_selector import ParameterSelector


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
                yield ParameterSelector()
            with TabPane("Launch", id="launch_tab"):
                yield LaunchTab()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tabbed_content.active == "parameters_tab":
            try:
                param_selector = self.query_one(ParameterSelector)
                param_selector.refresh_attacks()
            except Exception:
                pass
        elif event.tabbed_content.active == "launch_tab":
            try:
                launch_tab = self.query_one(LaunchTab)
                launch_tab.refresh_status()
            except Exception:
                pass



