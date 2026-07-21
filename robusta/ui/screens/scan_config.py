from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, TabbedContent, TabPane

from robusta.ui.widgets.attack_selector import AttackSelector
from robusta.ui.widgets.launch_tab import LaunchTab
from robusta.ui.widgets.model_selector_tab import ModelSelector
from robusta.ui.widgets.parameter_selector import ParameterSelector


class ScanConfigScreen(Screen):
    DEFAULT_CSS = """
    ScanConfigScreen {
        layout: vertical;
    }
    ScanConfigScreen TabbedContent {
        height: 1fr;
    }
    ScanConfigScreen ContentSwitcher {
        height: 1fr;
    }
    ScanConfigScreen TabPane {
        height: 1fr;
        padding: 0;
    }
    """

    BINDINGS = [
        ("ctrl+1", "switch_tab('model_dataset_tab')", "Model/Dataset"),
        ("ctrl+2", "switch_tab('attacks_tab')", "Attacks"),
        ("ctrl+3", "switch_tab('parameters_tab')", "Parameters"),
        ("ctrl+4", "switch_tab('launch_tab')", "Launch"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.scanner = self.app.scanner

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Model/Dataset", id="model_dataset_tab"):
                yield ModelSelector()
            with TabPane("Attacks", id="attacks_tab"):
                yield AttackSelector()
            with TabPane("Parameters", id="parameters_tab"):
                yield ParameterSelector()
            with TabPane("Launch", id="launch_tab"):
                yield LaunchTab()
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

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



