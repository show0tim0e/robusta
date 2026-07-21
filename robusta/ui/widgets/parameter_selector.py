from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Collapsible, Input, Label, ListItem, ListView, TabbedContent

from robusta.core.scanner import AttackConfig


class ParameterSelector(Horizontal):
    DEFAULT_CSS = """
    ParameterSelector {
        layout: horizontal;
        margin: 1 2;
        height: 100%;
    }

    #param-sidebar {
        width: 30%;
        height: 100%;
        border: round $accent;
        background: $surface;
        padding: 1 2;
        margin-right: 1;
    }

    #param-form-container {
        width: 70%;
        height: 100%;
        border: round $secondary;
        background: $surface;
        padding: 1 2;
    }

    .parameter-row {
        height: auto;
    }

    .parameter-row Input {
        border: none;
        height: 3;
        padding: 1;
    }

    .parameter-block {
        height: auto;
        margin-bottom: 1;
        border: round $primary;
        padding: 0 1;
    }

    .parameter-block Collapsible {
        margin-top: 0;
        border-top: none;
        padding-bottom: 0;
    }

    .parameter-block Collapsible Label {
        width: 100%;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.current_attack_config = None

    def on_mount(self) -> None:
        self.query_one("#param-sidebar").border_title = "Selected Attacks"
        self.query_one("#param-form-container").border_title = "Parameters"

    def compose(self) -> ComposeResult:
        with Vertical(id="param-sidebar"):
            yield ListView(id="selected-attacks-list")

        with Vertical(id="param-form-container"):
            yield VerticalScroll(id="param-fields")

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Automatically refresh selected attacks list when the Parameters tab is viewed."""
        if event.tab.id == "parameters_tab":
            self.refresh_attacks()

    def refresh_attacks(self) -> None:
        """Refresh the sidebar list of attacks from the scanner."""
        list_view = self.query_one("#selected-attacks-list", ListView)
        list_view.clear()

        if not hasattr(self.screen, "scanner") or not self.screen.scanner.attacks:
            self.current_attack_config = None
            self.query_one("#param-fields", Vertical).query("*").remove()
            self.query_one("#param-fields", Vertical).mount(
                Label("No attacks selected. Please select attacks in the Attacks tab first.", id="empty-state-label")
            )
            self.query_one("#param-form-container").border_title = "Parameters"
            return

        for attack_config in self.screen.scanner.attacks:
            attack_class = attack_config.attack
            item = ListItem(Label(attack_class.name()))
            item.attack_config = attack_config
            list_view.append(item)

        list_view.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when an attack is selected in the sidebar list."""
        item = event.item
        if not item or not hasattr(item, "attack_config"):
            return

        self._build_parameter_form(item.attack_config)

    def _build_parameter_form(self, attack_config: AttackConfig) -> None:
        """Dynamically build the input fields for the selected attack's parameters."""
        self.current_attack_config = attack_config
        attack_class = attack_config.attack
        params = attack_class.attack_parameters()

        container = self.query_one("#param-fields", VerticalScroll)
        container.query("*").remove()

        self.query_one("#param-form-container").border_title = f"Parameters: {attack_class.name()}"

        if not params:
            container.mount(Label("This attack has no parameters to configure.", id="no-params-label"))
            return

        for param in params:
            input_type = "text"
            if param.type is float:
                input_type = "number"
            elif param.type is int:
                input_type = "integer"

            val = attack_config.params.get(param.name, param.default)

            inp = Input(
                placeholder=str(param.default),
                id=f"param-{param.name}",
                type=input_type,
                value=str(val) if val is not None else "",
            )
            inp.param_name = param.name

            block_children: list = [Horizontal(inp, classes="parameter-row")]

            if param.description:
                block_children.append(
                    Collapsible(
                        Label(param.description),
                        title="Description",
                        collapsed=True,
                        id=f"param-desc-{param.name}",
                    )
                )

            block = Vertical(*block_children, classes="parameter-block")
            block.border_title = param.name
            container.mount(block)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called when any input value changes to sync it back to the scanner."""
        if not self.current_attack_config:
            return

        inp = event.input
        if not inp.id or not inp.id.startswith("param-"):
            return

        param_name = getattr(inp, "param_name", None)
        if not param_name:
            return

        attack_class = self.current_attack_config.attack
        params = attack_class.attack_parameters()
        param_def = next((p for p in params if p.name == param_name), None)
        if not param_def:
            return

        value_str = inp.value.strip()
        if not value_str:
            value = param_def.default
        else:
            try:
                if param_def.type is float:
                    value = float(value_str)
                elif param_def.type is int:
                    value = int(value_str)
                else:
                    value = value_str
            except ValueError:
                # Ignore failed parsing during typing
                return

        if hasattr(self.screen, "scanner"):
            current_configs = list(self.screen.scanner.attacks)
            for i, config in enumerate(current_configs):
                if config.attack == attack_class:
                    new_params = dict(config.params)
                    new_params[param_name] = value
                    current_configs[i] = AttackConfig(attack=attack_class, params=new_params)
                    self.current_attack_config = current_configs[i]
                    break

            self.screen.scanner.set_attacks(current_configs)