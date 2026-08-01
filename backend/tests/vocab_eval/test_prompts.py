import pytest
from experiments.vocab_eval.prompts import load_tutor_prompt, prompt_name, resolve_prompt_path


def test_resolve_prompt_path_finds_bundled_template():
    path = resolve_prompt_path("default")
    assert path.name == "default.txt"
    assert path.is_file()


def test_resolve_prompt_path_raises_for_unknown_name():
    with pytest.raises(FileNotFoundError):
        resolve_prompt_path("does-not-exist")


def test_load_tutor_prompt_fills_placeholders():
    prompt = load_tutor_prompt("default", language="Spanish", level="A1", topic="food")
    assert "Spanish" in prompt
    assert "A1" in prompt
    assert "food" in prompt
    assert "{language}" not in prompt


def test_prompt_name_returns_stem():
    assert prompt_name("default") == "default"
