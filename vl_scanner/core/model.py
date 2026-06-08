from dataclasses import dataclass
from pathlib import Path

from torch.nn import Module


@dataclass(slots=True)
class Model:
    path: str

    def __post_init__(self) -> None:
        candidate = Path(self.path)
        if not candidate.is_absolute():
            raise ValueError("Model path must be an absolute path.")

        self.path = str(candidate)

    def as_path(self) -> Path:
        return Path(self.path)

    def load(self) -> Module:
        pass