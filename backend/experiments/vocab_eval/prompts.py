"""Loading of tutor system prompt templates for vocab-eval experiments.

Templates are plain text files with {language}/{level}/{topic} placeholders,
looked up by name from the bundled prompt_templates/ directory (or an arbitrary path).
"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompt_templates"


def resolve_prompt_path(prompt: str) -> Path:
    """Resolve a prompt name (bundled) or explicit path to a template file.

    Args:
        prompt: Either the stem of a bundled template (e.g. "default" for
            prompt_templates/default.txt), or a path to an arbitrary template file.
    """
    explicit_path = Path(prompt)
    if explicit_path.is_file():
        return explicit_path

    bundled_path = PROMPTS_DIR / f"{prompt}.txt"
    if bundled_path.is_file():
        return bundled_path

    raise FileNotFoundError(
        f"No prompt template found for '{prompt}' (checked {explicit_path} and {bundled_path})"
    )


def load_tutor_prompt(prompt: str, language: str, level: str, topic: str) -> str:
    """Load a named/pathed tutor prompt template and fill in its placeholders."""
    path = resolve_prompt_path(prompt)
    template = path.read_text(encoding="utf-8")
    return template.format(language=language, level=level, topic=topic)


def prompt_name(prompt: str) -> str:
    """A filesystem-safe short name for a prompt, used in transcript filenames."""
    return resolve_prompt_path(prompt).stem
