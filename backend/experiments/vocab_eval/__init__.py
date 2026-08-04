"""Vocab-eval: LLM-as-judge research harness for tutor prompt/model comparison (issue #255).

Responsibilities:
    - Generate tutor/student-simulator conversation transcripts for a given
      (tutor model, prompt template) pair (`generate.py`).
    - Score a transcript's comprehensible-input ratio and vocabulary
      level-appropriateness using a second LLM as judge (`judge.py`).
    - Run the full (tutor model x prompt) matrix and write a summary CSV
      (`batch.py` — the entry point, run as `python -m experiments.vocab_eval.batch`).

Not exported: this package has no public API surface — it is a standalone
research spike, not a dependency of `app.*` production code. Import from the
specific submodule you need (`experiments.vocab_eval.generate`,
`experiments.vocab_eval.judge`, etc.) rather than from the package root.

Domain terms (Tutor, Student Simulator, Comprehensible Input Ratio,
LLM-as-Judge) are defined in `/CONTEXT.md` at the repo root — read that first.
Per-module docstrings hold the implementation detail; this file only orients.
"""
