"""Batch runner: generates + judges transcripts across a tutor-model x prompt matrix.

Standalone harness entry point for the vocab-eval research spike (issue #255).
Runs `generate_transcript` then `judge_transcript` for every (model, prompt)
combination and writes a summary CSV alongside the individual transcript and
verdict JSON files.
"""

import argparse
import asyncio
import csv
import logging
from pathlib import Path

from app.services.llm.providers.ollama import OllamaProvider
from experiments.vocab_eval.generate import generate_transcript
from experiments.vocab_eval.judge import default_judge_model, judge_transcript

logger = logging.getLogger(__name__)

DEFAULT_TUTOR_MODELS = [
    "llama3.2:latest",
    "qwen3:8b",
    "gemma4:latest",
    "mistral:7b",
    "phi4:latest",
]
DEFAULT_TUTOR_PROMPTS = ["variant_a", "variant_b"]

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RUN_DIR = REPO_ROOT / "tmp" / "vocab-eval"


async def run_matrix(
    tutor_models: list[str],
    tutor_prompts: list[str],
    language: str,
    level: str,
    topic: str,
    turns: int,
    judge_model: str | None,
    ollama_base_url: str,
    run_dir: Path,
) -> list[dict]:
    """Generate + judge one transcript per (model, prompt) combo. Returns summary rows."""
    transcripts_dir = run_dir / "transcripts"
    verdicts_dir = run_dir / "verdicts"
    rows: list[dict] = []

    for tutor_model in tutor_models:
        for tutor_prompt in tutor_prompts:
            logger.info("Generating: model=%s prompt=%s", tutor_model, tutor_prompt)
            transcript = await generate_transcript(
                tutor_model=tutor_model,
                tutor_prompt=tutor_prompt,
                language=language,
                level=level,
                topic=topic,
                turns=turns,
                ollama_base_url=ollama_base_url,
            )
            transcript_path = transcript.save(transcripts_dir)

            resolved_judge_model = judge_model or default_judge_model(tutor_model)
            judge_provider = OllamaProvider(base_url=ollama_base_url, model=resolved_judge_model)
            try:
                verdict = await judge_transcript(transcript, str(transcript_path), judge_provider)
            finally:
                await judge_provider.close()
            verdict_path = verdict.save(verdicts_dir)

            rows.append(
                {
                    "tutor_model": tutor_model,
                    "tutor_prompt": tutor_prompt,
                    "judge_model": resolved_judge_model,
                    "comprehensible_ratio": verdict.comprehensible_ratio,
                    "vocabulary_level_appropriate": verdict.vocabulary_level_appropriate,
                    "transcript_path": str(transcript_path),
                    "verdict_path": str(verdict_path),
                }
            )
            logger.info(
                "Judged: model=%s prompt=%s ratio=%.2f appropriate=%s",
                tutor_model,
                tutor_prompt,
                verdict.comprehensible_ratio,
                verdict.vocabulary_level_appropriate,
            )

    return rows


def write_summary_csv(rows: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tutor-models", nargs="+", default=DEFAULT_TUTOR_MODELS)
    parser.add_argument("--tutor-prompts", nargs="+", default=DEFAULT_TUTOR_PROMPTS)
    parser.add_argument("--language", default="Spanish")
    parser.add_argument("--level", default="A1")
    parser.add_argument("--topic", default="daily routines")
    parser.add_argument("--turns", type=int, default=8)
    parser.add_argument("--judge-model", default=None)
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> Path:
    args = parse_args(argv)
    rows = asyncio.run(
        run_matrix(
            tutor_models=args.tutor_models,
            tutor_prompts=args.tutor_prompts,
            language=args.language,
            level=args.level,
            topic=args.topic,
            turns=args.turns,
            judge_model=args.judge_model,
            ollama_base_url=args.ollama_base_url,
            run_dir=args.run_dir,
        )
    )
    summary_path = write_summary_csv(rows, args.run_dir / "summary.csv")
    logger.info("Wrote summary to %s", summary_path)
    return summary_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
