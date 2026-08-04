from pathlib import Path

from experiments.vocab_eval.transcript import Transcript, Turn


def make_transcript(**overrides) -> Transcript:
    defaults = dict(
        language="Spanish",
        level="A1",
        topic="food",
        tutor_model="llama3.2:latest",
        tutor_prompt_name="default",
        student_model="llama3.2:latest",
        turns=[Turn(role="tutor", content="Hola!"), Turn(role="student", content="Hola, gracias!")],
    )
    defaults.update(overrides)
    return Transcript(**defaults)


def test_save_writes_json_file_under_output_dir(tmp_path: Path):
    transcript = make_transcript()

    path = transcript.save(output_dir=tmp_path)

    assert path.parent == tmp_path
    assert path.exists()
    assert path.suffix == ".json"


def test_save_filename_sanitizes_model_name(tmp_path: Path):
    transcript = make_transcript(tutor_model="qwen3:8b")

    path = transcript.save(output_dir=tmp_path)

    assert "qwen3-8b" in path.name
    assert ":" not in path.name


def test_load_round_trips_turns(tmp_path: Path):
    transcript = make_transcript()
    path = transcript.save(output_dir=tmp_path)

    loaded = Transcript.load(path)

    assert loaded.language == transcript.language
    assert loaded.tutor_model == transcript.tutor_model
    assert [t.role for t in loaded.turns] == [t.role for t in transcript.turns]
    assert [t.content for t in loaded.turns] == [t.content for t in transcript.turns]
