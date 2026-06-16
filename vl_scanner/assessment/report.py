from typing import Any


class Report:
    def build(
        self,
        clean: dict[str, float],
        attacks: dict[str, dict[str, float]],
    ) -> dict[str, Any]:
        pass