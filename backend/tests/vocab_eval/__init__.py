"""Tests for `experiments.vocab_eval` (see that package's docstring for scope).

One test module per source module (`test_generate.py` <-> `generate.py`, etc.).
No shared fixtures live here; each test module fakes the Ollama-backed
`LLMProvider` it needs (via `monkeypatch` + a local `FakeProvider`) rather
than hitting a running Ollama instance.
"""
