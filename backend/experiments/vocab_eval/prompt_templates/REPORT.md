# Prompt template comparison report

Consolidated, judged comparison of `default.txt` vs `variant_a.txt` vs
`variant_b.txt` (see `README.md` for what each template does).

**Status: not yet generated.** This file is a template — running the batch
harness against a real Ollama instance produces the actual data. It is not
regenerated automatically; re-run and replace this file's content whenever
the templates or default tutor/judge models change materially.

## How to regenerate

```bash
cd backend
uv run python -m experiments.vocab_eval.batch \
  --tutor-prompts default variant_a variant_b \
  --tutor-models llama3.2:latest \
  --language Spanish --level A1 --topic "daily routines" \
  --run-dir ../tmp/vocab-eval/report-run
```

Then fill in the table below from `tmp/vocab-eval/report-run/summary.csv`,
and commit this file so the comparison is readable without a local dev
environment.

## Results

| Generated at (UTC) | Tutor model | Prompt | Judge model | Comprehensible ratio | Vocabulary level-appropriate |
|---|---|---|---|---|---|
| _pending_ | | | | | |

## Notes

- One tutor model (`llama3.2:latest`) is enough to compare templates in
  isolation; the full `DEFAULT_TUTOR_MODELS` matrix conflates
  template quality with tutor-model quality (see README's "Tutor vs. judge
  model suitability" section) and is a separate question.
- A single transcript per (model, prompt) is one sample, not a statistically
  reliable comparison — treat this report as directional, not conclusive.
