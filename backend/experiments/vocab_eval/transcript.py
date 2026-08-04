"""Transcript data model and JSON persistence for vocab-eval conversations."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRANSCRIPTS_DIR = REPO_ROOT / "tmp" / "vocab-eval" / "transcripts"


@dataclass
class Turn:
    """One utterance in a student/tutor conversation."""

    role: str  # "tutor" or "student"
    content: str


@dataclass
class Transcript:
    """A full generated conversation plus the config that produced it."""

    language: str
    level: str
    topic: str
    tutor_model: str
    tutor_prompt_name: str
    student_model: str
    turns: list[Turn] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, output_dir: Path | None = None) -> Path:
        """Write this transcript to a JSON file and return its path."""
        output_dir = output_dir or DEFAULT_TRANSCRIPTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_tutor_model = self.tutor_model.replace(":", "-").replace("/", "-")
        filename = (
            f"{timestamp}_{self.language.lower()}_{self.level.lower()}_"
            f"{safe_tutor_model}_{self.tutor_prompt_name}.json"
        )
        path = output_dir / filename
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "Transcript":
        data = json.loads(path.read_text(encoding="utf-8"))
        turns = [Turn(**t) for t in data.pop("turns", [])]
        return cls(turns=turns, **data)
