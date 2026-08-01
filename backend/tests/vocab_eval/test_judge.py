import json
from pathlib import Path

import pytest
from experiments.vocab_eval import judge as judge_module
from experiments.vocab_eval.judge import (
    Verdict,
    default_judge_model,
    judge_transcript,
    main,
    parse_verdict_json,
    render_transcript_for_judge,
)
from experiments.vocab_eval.transcript import Transcript, Turn

from app.services.llm.base import LLMResponse


class FakeJudgeProvider:
    def __init__(self, model: str, reply: str):
        self._model = model
        self._reply = reply
        self.calls: list[tuple[list[dict[str, str]], str]] = []
        self.closed = False

    @property
    def name(self) -> str:
        return "fake"

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, messages, system_prompt, max_tokens=1000, temperature=0.7):
        self.calls.append((list(messages), system_prompt))
        return LLMResponse(content=self._reply, model=self._model)

    async def generate_stream(self, *args, **kwargs):
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        self.closed = True


def make_transcript() -> Transcript:
    return Transcript(
        language="Spanish",
        level="A1",
        topic="food",
        tutor_model="llama3.2:latest",
        tutor_prompt_name="variant_a",
        student_model="llama3.2:latest",
        turns=[
            Turn(role="tutor", content="Hola, ¿tienes hambre?"),
            Turn(role="student", content="Sí, tengo hambre."),
        ],
    )


def test_render_transcript_for_judge_includes_role_and_content():
    rendered = render_transcript_for_judge(make_transcript())
    assert "TUTOR: Hola, ¿tienes hambre?" in rendered
    assert "STUDENT: Sí, tengo hambre." in rendered


def test_parse_verdict_json_strips_markdown_fences():
    raw = '```json\n{"comprehensible_ratio": 0.8, "vocabulary_level_appropriate": true}\n```'
    data = parse_verdict_json(raw)
    assert data == {"comprehensible_ratio": 0.8, "vocabulary_level_appropriate": True}


def test_parse_verdict_json_raises_when_no_json_present():
    with pytest.raises(ValueError):
        parse_verdict_json("no json here")


@pytest.mark.parametrize(
    ("tutor_model", "expected_not"),
    [
        ("llama3.2:latest", None),
        (judge_module.DEFAULT_JUDGE_MODEL, judge_module.DEFAULT_JUDGE_MODEL),
    ],
)
def test_default_judge_model_never_matches_tutor_model(tutor_model, expected_not):
    result = default_judge_model(tutor_model)
    assert result != tutor_model
    if expected_not:
        assert result != expected_not


@pytest.mark.asyncio
async def test_judge_transcript_parses_structured_verdict():
    reply = json.dumps(
        {
            "comprehensible_ratio": 0.85,
            "vocabulary_level_appropriate": True,
            "new_vocabulary": ["hambre"],
            "reasoning": "Mostly A1 vocabulary with one inferable new word.",
        }
    )
    provider = FakeJudgeProvider(model="llama3.1:8b", reply=reply)

    verdict = await judge_transcript(make_transcript(), "some/path.json", provider)

    assert verdict.transcript_path == "some/path.json"
    assert verdict.judge_model == "llama3.1:8b"
    assert verdict.comprehensible_ratio == 0.85
    assert verdict.vocabulary_level_appropriate is True
    assert verdict.new_vocabulary == ["hambre"]
    assert verdict.reasoning == "Mostly A1 vocabulary with one inferable new word."
    assert provider.calls[0][1].startswith("You are an expert CEFR language-assessment judge")


def test_verdict_save_writes_json_file_under_output_dir(tmp_path: Path):
    verdict = Verdict(
        transcript_path="x.json",
        judge_model="llama3.1:8b",
        comprehensible_ratio=0.7,
        vocabulary_level_appropriate=False,
        new_vocabulary=["perro"],
        reasoning="too many new words",
    )

    path = verdict.save(tmp_path)

    assert path.exists()
    assert path.parent == tmp_path
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["comprehensible_ratio"] == 0.7


def test_main_writes_verdict_file(tmp_path: Path, monkeypatch, caplog):
    make_transcript().save(tmp_path)
    transcript_path = next(tmp_path.glob("*.json"))

    reply = json.dumps(
        {
            "comprehensible_ratio": 0.9,
            "vocabulary_level_appropriate": True,
            "new_vocabulary": [],
            "reasoning": "fine",
        }
    )

    class FakeOllamaProvider(FakeJudgeProvider):
        def __init__(self, base_url: str, model: str):
            super().__init__(model=model, reply=reply)

    monkeypatch.setattr(judge_module, "OllamaProvider", FakeOllamaProvider)

    output_dir = tmp_path / "verdicts"
    with caplog.at_level("INFO"):
        path = main(
            [
                str(transcript_path),
                "--judge-model",
                "llama3.1:8b",
                "--output-dir",
                str(output_dir),
            ]
        )

    assert path.exists()
    assert path.parent == output_dir
    assert str(path) in caplog.text
