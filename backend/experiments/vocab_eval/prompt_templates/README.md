# prompt_templates

Tutor system-prompt templates for the vocab-eval harness (issue #255). Each
`.txt` file is a Python `str.format`-style template filled in by
`prompts.load_tutor_prompt()` with `{language}`, `{level}`, `{topic}`.

Selected by stem name via `--tutor-prompt <name>` on `generate.py` and
`batch.py` (or an explicit path to a template outside this directory).

## Templates

| Template | Approach |
|---|---|
| `default.txt` | Minimal baseline: level-appropriate vocabulary, short responses, one new word per turn, implicit correction. |
| `variant_a.txt` | Stricter "Level+1" constraints (top-500-word vocabulary, 5-10 word sentences, present tense only) plus an explicit error-correction script. |
| `variant_b.txt` | Same Level+1 target ratio as `variant_a` but framed around teaching philosophy/encouragement first, with a more detailed correction script. |

Compare template output with the batch runner (below); which one wins is a
judged, empirical question — not decided by reading the prompts.

## Running the harness

`batch.py` is the entry point — the "main loop" that runs the full
(tutor model x prompt) matrix and writes a summary CSV:

```bash
cd backend
uv run python -m experiments.vocab_eval.batch \
  --tutor-prompts default variant_a variant_b \
  --language Spanish --level A1 --topic "daily routines"
```

Requires a local Ollama instance (`--ollama-base-url`, default
`http://localhost:11434`) with the tutor/judge/student models pulled.
Output (transcripts, verdicts, `summary.csv`) is written under
`tmp/vocab-eval/` by default.

## Tutor vs. judge model suitability

`batch.py`'s `DEFAULT_TUTOR_MODELS` mixes general-purpose chat models
(`llama3.2`, `qwen3:8b`, `gemma4`, `mistral:7b`) with `phi4`, which Microsoft
positions primarily for math/code/reasoning rather than open-domain
conversation. It's included deliberately as a lower-conversational-fluency
control point, not because it's expected to be a strong tutor: a
weaker-at-conversation model tutoring is a different failure mode than a
weak *student*, and the matrix should surface that as a low
`vocabulary_level_appropriate` / erratic `comprehensible_ratio` score rather
than assuming it in advance.

The judge (`judge.py`, default `llama3.1:8b`) only needs to *evaluate*
comprehensible-input ratio and level-appropriateness against a rubric, not
converse fluently — reasoning-oriented models are plausible judge candidates
for that reason, not ruled out the way they might be as a tutor. This
harness does not yet include a judge-model comparison (calibrating verdicts
across candidate judges against a human reading); that is future work for
this research spike, not a decision baked into the current default.
