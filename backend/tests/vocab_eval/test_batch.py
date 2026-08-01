import csv
import json
from pathlib import Path

import pytest

from app.services.llm.base import LLMResponse
from experiments.vocab_eval import batch as batch_module
from experiments.vocab_eval.batch import main, run_matrix, write_summary_csv


class FakeOllamaProvider:
    """Returns a scripted tutor/student reply, or a scripted judge JSON verdict."""

    def __init__(self, base_url: str, model: str):
        self.model_ = model
        self.calls = 0

    @property
    def name(self) -> str:
        return "fake"

    @property
    def model(self) -> str:
        return self.model_

    async def generate(self, messages, system_prompt, max_tokens=1000, temperature=0.7):
        self.calls += 1
        if "CEFR language-assessment judge" in system_prompt:
            return LLMResponse(
                content=json.dumps(
                    {
                        "comprehensible_ratio": 0.82,
                        "vocabulary_level_appropriate": True,
                        "new_vocabulary": ["hola"],
                        "reasoning": "fine",
                    }
                ),
                model=self.model_,
            )
        return LLMResponse(content=f"reply-{self.calls}", model=self.model_)

    async def generate_stream(self, *args, **kwargs):
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_run_matrix_generates_and_judges_every_combo(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(batch_module, "OllamaProvider", FakeOllamaProvider)
    import experiments.vocab_eval.generate as generate_module

    monkeypatch.setattr(generate_module, "OllamaProvider", FakeOllamaProvider)

    rows = await run_matrix(
        tutor_models=["model-a", "model-b"],
        tutor_prompts=["variant_a", "variant_b"],
        language="Spanish",
        level="A1",
        topic="food",
        turns=1,
        judge_model="judge-model",
        ollama_base_url="http://localhost:11434",
        run_dir=tmp_path,
    )

    assert len(rows) == 4
    combos = {(r["tutor_model"], r["tutor_prompt"]) for r in rows}
    assert combos == {
        ("model-a", "variant_a"),
        ("model-a", "variant_b"),
        ("model-b", "variant_a"),
        ("model-b", "variant_b"),
    }
    assert all(r["judge_model"] == "judge-model" for r in rows)
    assert all(Path(r["transcript_path"]).exists() for r in rows)
    assert all(Path(r["verdict_path"]).exists() for r in rows)


def test_write_summary_csv_writes_header_and_rows(tmp_path: Path):
    rows = [
        {"tutor_model": "a", "comprehensible_ratio": 0.8},
        {"tutor_model": "b", "comprehensible_ratio": 0.6},
    ]
    path = write_summary_csv(rows, tmp_path / "summary.csv")

    with path.open(encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert [r["tutor_model"] for r in reader] == ["a", "b"]


def test_write_summary_csv_handles_empty_rows(tmp_path: Path):
    path = write_summary_csv([], tmp_path / "summary.csv")
    assert path.exists()
    assert path.read_text(encoding="utf-8").strip() == ""


def test_main_writes_summary_csv(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(batch_module, "OllamaProvider", FakeOllamaProvider)
    import experiments.vocab_eval.generate as generate_module

    monkeypatch.setattr(generate_module, "OllamaProvider", FakeOllamaProvider)

    path = main(
        [
            "--tutor-models",
            "model-a",
            "--tutor-prompts",
            "variant_a",
            "--turns",
            "1",
            "--judge-model",
            "judge-model",
            "--run-dir",
            str(tmp_path),
        ]
    )

    assert path.exists()
    assert path == tmp_path / "summary.csv"
