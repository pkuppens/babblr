from experiments.vocab_eval.student import build_student_prompt


def test_build_student_prompt_fills_placeholders():
    prompt = build_student_prompt(language="Spanish", level="A1", topic="food")
    assert "Spanish" in prompt
    assert "A1" in prompt
    assert "food" in prompt
