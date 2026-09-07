# Writing style: Simplified Technical English

Babblr is multilingual by nature. Keep the product and its history easy to read
and to translate. Write all natural language in **ASD-STE100 Simplified
Technical English (STE)**, unless a task says otherwise.

ASD-STE100 is the Simplified Technical English specification from the AeroSpace
and Defence Industries Association of Europe (ASD). This file gives a working
summary, not the full specification.

## Where STE applies

- Code comments and docstrings
- Names of variables, functions, classes, and files, as far as clear English allows
- Commit messages, pull request titles and descriptions
- Issue text and code review comments
- Repository documentation (Markdown files)
- English user-facing interface text that the app shows

## STE rules in short

- Use short sentences. Keep procedure sentences to 20 words or fewer. Keep
  descriptive sentences to 25 words or fewer.
- Keep each instruction to one action. Start a procedure step with the verb.
- Use the active voice. Write "Run the tests", not "The tests should be run".
- Use simple tenses (past, present, future). Do not use the present perfect or
  the future perfect.
- Use common, approved words. Use one word for one meaning, and one meaning for
  one word.
- Keep articles ("the", "a") and other short words that make the sentence clear.
  Do not drop them.
- Do not make noun clusters of more than three words. Break
  "backend test runner cache key" into a phrase with prepositions.
- Avoid idioms, slang, phrasal verbs, and Latin abbreviations ("e.g.", "i.e.",
  "etc."). Write "for example", "that is", "and so on".
- Write positive instructions. State what to do, not only what to avoid.

### Examples

| Not STE | STE |
| --- | --- |
| The provider should be registered in the factory so that it can be resolved. | Register the provider in the factory. The factory then resolves it. |
| We've now removed the deprecated call. | This change removes the deprecated call. |
| Kick off the build and keep an eye on CI. | Start the build. Watch the CI run. |

## Where STE does not apply

- Language-learning content and example dialogues in the target languages
  (Spanish, Italian, German, French, Dutch, English).
- English content that a task asks for at a set CEFR level, most notably C1-C2
  tutor material. Write this content to the conventions of that level instead.
- Third-party text that you quote without change (error messages, library
  output, text from a standard).

When you are not sure whether STE applies, ask.

## Shell scripts

Never use Unicode or emoji in `.sh` or `.bat` files. Use ASCII status prefixes:

- `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[SETUP]`, `[START]`
