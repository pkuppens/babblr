"""LLM-as-judge scorer for vocab-eval transcripts.

Scores a generated tutor/student transcript for comprehensible-input ratio
and level-appropriateness of new vocabulary, using a configurable judge
model + prompt. Standalone: does not touch production conversation code.
"""

import argparse
import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.services.llm.base import LLMProvider
from app.services.llm.providers.ollama import OllamaProvider
from experiments.vocab_eval.transcript import Transcript

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VERDICTS_DIR = REPO_ROOT / "tmp" / "vocab-eval" / "verdicts"

# Distinct from every model in the tutor matrix (llama3.2:latest, qwen3:8b,
# gemma4:latest, mistral:7b, phi4:latest) so the judge never scores itself.
DEFAULT_JUDGE_MODEL = "llama3.1:8b"

JUDGE_SYSTEM_PROMPT = """You are an expert CEFR language-assessment judge. You will be shown a \
transcript of a conversation between a language tutor and a student, and the student's target \
level. Judge ONLY the tutor's turns.

Assess two things:
1. Comprehensible-input ratio: the fraction (0.0-1.0) of the tutor's words/phrases that a \
{level} {language} student would be expected to understand. Comprehensible-input research \
targets roughly 80% (0.8) known material with the rest being learnable-from-context stretch \
vocabulary.
2. Whether new (not-yet-known) vocabulary introduced by the tutor is level-appropriate for a \
{level} student (i.e. simple, high-frequency, inferable from context) rather than jumping far \
above the student's level.

Respond with ONLY a JSON object (no markdown fences, no commentary) with exactly these keys:
{{
  "comprehensible_ratio": <float 0.0-1.0>,
  "vocabulary_level_appropriate": <true|false>,
  "new_vocabulary": [<list of new words/phrases the tutor introduced>],
  "reasoning": <short string explaining the scores>
}}"""


@dataclass
class Verdict:
    """A judge's structured assessment of one transcript."""

    transcript_path: str
    judge_model: str
    comprehensible_ratio: float
    vocabulary_level_appropriate: bool
    new_vocabulary: list[str] = field(default_factory=list)
    reasoning: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, output_dir: Path | None = None) -> Path:
        """Write this verdict to a JSON file and return its path."""
        output_dir = output_dir or DEFAULT_VERDICTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        source_stem = Path(self.transcript_path).stem
        safe_judge_model = self.judge_model.replace(":", "-").replace("/", "-")
        filename = f"{timestamp}_{source_stem}_judged-by_{safe_judge_model}.json"
        path = output_dir / filename
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def default_judge_model(tutor_model: str) -> str:
    """Pick a judge model distinct from the tutor model being evaluated."""
    if tutor_model != DEFAULT_JUDGE_MODEL:
        return DEFAULT_JUDGE_MODEL
    return "gemma4:latest" if tutor_model != "gemma4:latest" else "mistral:7b"


def render_transcript_for_judge(transcript: Transcript) -> str:
    """Render a transcript's turns as plain text for the judge prompt."""
    lines = [f"{turn.role.upper()}: {turn.content}" for turn in transcript.turns]
    return "\n".join(lines)


def parse_verdict_json(raw: str) -> dict:
    """Extract a JSON object from a judge response, tolerating markdown fences."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in judge response: {raw!r}")
    return json.loads(match.group(0))


async def judge_transcript(
    transcript: Transcript,
    transcript_path: str,
    judge_provider: LLMProvider,
) -> Verdict:
    """Score a transcript using the given judge provider, returning a structured Verdict."""
    system_prompt = JUDGE_SYSTEM_PROMPT.format(language=transcript.language, level=transcript.level)
    conversation = render_transcript_for_judge(transcript)
    response = await judge_provider.generate(
        messages=[{"role": "user", "content": conversation}],
        system_prompt=system_prompt,
    )
    data = parse_verdict_json(response.content)

    return Verdict(
        transcript_path=transcript_path,
        judge_model=judge_provider.model,
        comprehensible_ratio=float(data["comprehensible_ratio"]),
        vocabulary_level_appropriate=bool(data["vocabulary_level_appropriate"]),
        new_vocabulary=list(data.get("new_vocabulary", [])),
        reasoning=str(data.get("reasoning", "")),
    )


async def judge_transcript_file(
    transcript_path: Path,
    judge_model: str | None,
    ollama_base_url: str,
) -> Verdict:
    transcript = Transcript.load(transcript_path)
    resolved_judge_model = judge_model or default_judge_model(transcript.tutor_model)
    judge_provider = OllamaProvider(base_url=ollama_base_url, model=resolved_judge_model)
    try:
        return await judge_transcript(transcript, str(transcript_path), judge_provider)
    finally:
        await judge_provider.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="Path to a transcript JSON file")
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Ollama model to use as judge (default: a model distinct from the tutor)",
    )
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> Path:
    args = parse_args(argv)
    verdict = asyncio.run(
        judge_transcript_file(
            transcript_path=args.transcript,
            judge_model=args.judge_model,
            ollama_base_url=args.ollama_base_url,
        )
    )
    path = verdict.save(args.output_dir)
    logger.info("Saved verdict to %s", path)
    return path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
