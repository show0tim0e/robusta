from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Label, SelectionList

from vl_scanner.attacks import Attack
from vl_scanner.core.scanner import AttackConfig


class AttackSelector(Horizontal):
    DEFAULT_CSS = """
    AttackSelector {
        layout: horizontal;
        margin: 1 2;
        height: 100%;
    }

    #attack-list-container {
        width: 40%;
        height: 100%;
        border: round $accent;
        background: $surface;
        padding: 1 2;
        margin-right: 1;
    }

    #attack-list-view {
        height: 1fr;
    }

    #attack-description-container {
        width: 60%;
        height: 100%;
        border: round $secondary;
        background: $surface;
        padding: 1 2;
    }

    #attack-description {
        width: 100%;
    }
    """

    def on_mount(self) -> None:
        self.query_one("#attack-list-container").border_title = "Select Attacks"
        self.query_one("#attack-description-container").border_title = "Description"

        list_widget = self.query_one("#attack-list-view", SelectionList)

        # Set initial description for the first item
        if list_widget.option_count > 0:
            first_attack = list_widget.get_option_at_index(0).value
            self.query_one("#attack-description", Label).update(first_attack.description())

    def compose(self) -> ComposeResult:
        # View 1: The Attack List
        with Container(id="attack-list-container"):
            yield SelectionList(
                *[(attack.name(), attack) for attack in Attack.registry.values()],
                id="attack-list-view",
            )

        # View 2: The Description Panel
        with VerticalScroll(id="attack-description-container"):
            yield Label("Select an attack to see its description.", id="attack-description")

    def on_selection_list_selection_highlighted(
        self, event: SelectionList.SelectionHighlighted
    ) -> None:
        """Update the description box when the highlight changes."""
        attack_class = event.selection_list.get_option_at_index(event.selection_index).value
        description = attack_class.description()
        self.query_one("#attack-description", Label).update(description)

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        """Update the scanner's configured attacks when the selection changes."""
        selected_attacks = event.selection_list.selected
        configs = []
        for attack_class in selected_attacks:
            # Generate AttackConfig with defaults
            params = {p.name: p.default for p in attack_class.attack_parameters()}
            configs.append(AttackConfig(attack=attack_class, params=params))

        self.app.scanner.set_attacks(configs)

        from vl_scanner.ui.widgets.launch_tab import LaunchTab
        try:
            self.screen.query_one(LaunchTab).refresh_status()
        except Exception:
            pass