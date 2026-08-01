from pathlib import Path

import pytest

from app.services.llm.base import LLMResponse
from experiments.vocab_eval import generate as generate_module
from experiments.vocab_eval.generate import generate_transcript, main, run_conversation


class FakeProvider:
    """Records calls and returns a scripted reply per call, for a given role."""

    def __init__(self, role: str, model: str = "fake-model"):
        self.role = role
        self._model = model
        self.calls: list[list[dict[str, str]]] = []
        self.closed = False

    @property
    def name(self) -> str:
        return "fake"

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, messages, system_prompt, max_tokens=1000, temperature=0.7):
        self.calls.append(list(messages))
        return LLMResponse(content=f"{self.role}-reply-{len(self.calls)}", model=self._model)

    async def generate_stream(self, *args, **kwargs):
        raise NotImplementedError

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_run_conversation_alternates_tutor_and_student_turns():
    tutor = FakeProvider("tutor")
    student = FakeProvider("student")

    turns = await run_conversation(
        tutor_provider=tutor,
        student_provider=student,
        tutor_system_prompt="tutor system prompt",
        student_system_prompt="student system prompt",
        turns=3,
    )

    assert [t.role for t in turns] == ["tutor", "student"] * 3
    assert turns[0].content == "tutor-reply-1"
    assert turns[1].content == "student-reply-1"
    assert len(tutor.calls) == 3
    assert len(student.calls) == 3
    # student's second call should see the tutor's second reply as the latest user message
    assert student.calls[1][-1] == {"role": "user", "content": "tutor-reply-2"}


@pytest.mark.asyncio
async def test_run_conversation_zero_turns_produces_no_turns():
    tutor = FakeProvider("tutor")
    student = FakeProvider("student")

    turns = await run_conversation(
        tutor_provider=tutor,
        student_provider=student,
        tutor_system_prompt="x",
        student_system_prompt="y",
        turns=0,
    )

    assert turns == []


@pytest.mark.asyncio
async def test_generate_transcript_fixes_student_model_regardless_of_tutor_model(monkeypatch):
    created: list[tuple[str, str]] = []

    class FakeOllamaProvider(FakeProvider):
        def __init__(self, base_url: str, model: str):
            role = "student" if model == generate_module.STUDENT_MODEL else "tutor"
            super().__init__(role, model=model)
            created.append((base_url, model))

    monkeypatch.setattr(generate_module, "OllamaProvider", FakeOllamaProvider)

    transcript = await generate_transcript(
        tutor_model="qwen3:8b",
        tutor_prompt="default",
        language="Spanish",
        level="A1",
        topic="food",
        turns=2,
        ollama_base_url="http://localhost:11434",
    )

    assert transcript.tutor_model == "qwen3:8b"
    assert transcript.student_model == generate_module.STUDENT_MODEL
    assert transcript.tutor_prompt_name == "default"
    assert len(transcript.turns) == 4
    models_created = {model for _, model in created}
    assert models_created == {"qwen3:8b", generate_module.STUDENT_MODEL}


def test_main_writes_transcript_file(tmp_path: Path, monkeypatch, caplog):
    class FakeOllamaProvider(FakeProvider):
        def __init__(self, base_url: str, model: str):
            role = "student" if model == generate_module.STUDENT_MODEL else "tutor"
            super().__init__(role, model=model)

    monkeypatch.setattr(generate_module, "OllamaProvider", FakeOllamaProvider)

    with caplog.at_level("INFO"):
        path = main(
            [
                "--tutor-model",
                "llama3.2:latest",
                "--turns",
                "1",
                "--output-dir",
                str(tmp_path),
            ]
        )

    assert path.exists()
    assert path.parent == tmp_path
    assert str(path) in caplog.text
