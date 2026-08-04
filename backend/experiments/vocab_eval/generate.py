"""Vocab-eval transcript generation harness.

Drives a conversation between a fixed student-simulator model and a
configurable tutor (model + prompt template), and saves the transcript
to tmp/vocab-eval/transcripts/. Standalone: does not touch
app.services.conversation_service, PromptBuilder, or ModularPromptBuilder.
"""

import argparse
import asyncio
import logging
from pathlib import Path

from app.services.llm.base import LLMProvider
from app.services.llm.providers.ollama import OllamaProvider
from experiments.vocab_eval.prompts import load_tutor_prompt, prompt_name
from experiments.vocab_eval.student import build_student_prompt
from experiments.vocab_eval.transcript import Transcript, Turn

STUDENT_MODEL = "llama3.2:latest"

logger = logging.getLogger(__name__)


async def run_conversation(
    tutor_provider: LLMProvider,
    student_provider: LLMProvider,
    tutor_system_prompt: str,
    student_system_prompt: str,
    turns: int,
) -> list[Turn]:
    """Generate `turns` tutor/student exchange pairs and return them in order."""
    result: list[Turn] = []
    tutor_messages: list[dict[str, str]] = []
    student_messages: list[dict[str, str]] = []

    for _ in range(turns):
        tutor_reply = await tutor_provider.generate(
            messages=tutor_messages, system_prompt=tutor_system_prompt
        )
        tutor_text = tutor_reply.content
        result.append(Turn(role="tutor", content=tutor_text))
        tutor_messages.append({"role": "assistant", "content": tutor_text})
        student_messages.append({"role": "user", "content": tutor_text})

        student_reply = await student_provider.generate(
            messages=student_messages, system_prompt=student_system_prompt
        )
        student_text = student_reply.content
        result.append(Turn(role="student", content=student_text))
        student_messages.append({"role": "assistant", "content": student_text})
        tutor_messages.append({"role": "user", "content": student_text})

    return result


async def generate_transcript(
    tutor_model: str,
    tutor_prompt: str,
    language: str,
    level: str,
    topic: str,
    turns: int,
    ollama_base_url: str,
) -> Transcript:
    tutor_provider = OllamaProvider(base_url=ollama_base_url, model=tutor_model)
    student_provider = OllamaProvider(base_url=ollama_base_url, model=STUDENT_MODEL)

    tutor_system_prompt = load_tutor_prompt(tutor_prompt, language, level, topic)
    student_system_prompt = build_student_prompt(language, level, topic)

    try:
        turn_list = await run_conversation(
            tutor_provider, student_provider, tutor_system_prompt, student_system_prompt, turns
        )
    finally:
        await tutor_provider.close()
        await student_provider.close()

    return Transcript(
        language=language,
        level=level,
        topic=topic,
        tutor_model=tutor_model,
        tutor_prompt_name=prompt_name(tutor_prompt),
        student_model=STUDENT_MODEL,
        turns=turn_list,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tutor-model", default="llama3.2:latest")
    parser.add_argument(
        "--tutor-prompt", default="default", help="Bundled prompt name or path to a template file"
    )
    parser.add_argument("--language", default="Spanish")
    parser.add_argument("--level", default="A1")
    parser.add_argument("--topic", default="daily routines")
    parser.add_argument(
        "--turns", type=int, default=8, help="Number of tutor/student exchange pairs"
    )
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> Path:
    args = parse_args(argv)
    transcript = asyncio.run(
        generate_transcript(
            tutor_model=args.tutor_model,
            tutor_prompt=args.tutor_prompt,
            language=args.language,
            level=args.level,
            topic=args.topic,
            turns=args.turns,
            ollama_base_url=args.ollama_base_url,
        )
    )
    path = transcript.save(args.output_dir)
    logger.info("Saved transcript to %s", path)
    return path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
