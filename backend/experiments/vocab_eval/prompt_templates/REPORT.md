# Prompt template comparison report

Consolidated, judged comparison of `default.txt` vs `variant_a.txt` vs
`variant_b.txt` (see `README.md` for what each template does).

**Status: generated 2026-08-02.** Single-sample run (see "Notes"); re-run and
replace this file's content whenever the templates or default tutor/judge
models change materially — it is not regenerated automatically.

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

Tutor: `llama3.2:latest`. Judge: `llama3.1:8b`. Language: Spanish, Level: A1,
Topic: "daily routines", 8 turns.

| Generated at (UTC) | Prompt | Comprehensible ratio | Vocabulary level-appropriate | New vocabulary introduced |
|---|---|---|---|---|
| 2026-08-02T08:05:55Z | `default` | 0.95 | True | amor, biblioteca, césped, soleado, alma |
| 2026-08-02T08:06:11Z | `variant_a` | 0.90 | True | narrativa, relajarme con las historias |
| 2026-08-02T08:06:33Z | `variant_b` | 0.85 | True | polvo de hornear, miele, crema chantillí |

Judge reasoning (verbatim, abridged):

- **default**: "The tutor's input is mostly at the A1 level... some new
  vocabulary introduced by the tutor... may be slightly above the A1 level
  in terms of frequency or complexity."
- **variant_a**: "The tutor's language is generally at the A1 level... The
  only instances of potentially challenging vocabulary... may require some
  inference or contextual guessing... not excessively complex or beyond the
  student's level."
- **variant_b** (judge responded in Spanish for this run): "El tutor
  utiliza un lenguaje claro y comprensible para la mayoría del diálogo, con
  algunas excepciones como el uso de vocabulario avanzado... La proporción
  de vocabulario nuevo es moderada, pero se infiere con facilidad a partir
  del contexto."

Full transcripts and verdict JSON are under `tmp/vocab-eval/report-run/`
(gitignored, not committed — regenerate locally to inspect).

## Notes

- One tutor model (`llama3.2:latest`) is enough to compare templates in
  isolation; the full `DEFAULT_TUTOR_MODELS` matrix conflates
  template quality with tutor-model quality (see README's "Tutor vs. judge
  model suitability" section) and is a separate question.
- A single transcript per (model, prompt) is one sample, not a statistically
  reliable comparison — treat this report as directional, not conclusive.
  On this run, `default` scored highest on comprehensible ratio and
  `variant_b` lowest, but all three passed the vocabulary-appropriateness
  check; the stricter Level+1 framing in `variant_a`/`variant_b` didn't
  translate into a measurably higher ratio here.
- The judge occasionally switches to responding in the target language
  (Spanish, for `variant_b` above) despite an English system prompt, and one
  run produced a mis-encoded character in `new_vocabulary` ("crema
  chantill<mojibake>" — likely "chantillí"). Neither affected the
  structured `comprehensible_ratio`/`vocabulary_level_appropriate` fields,
  but both are worth a closer look if this harness graduates beyond a
  research spike.
