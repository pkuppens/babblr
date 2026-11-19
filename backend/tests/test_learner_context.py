"""Tests for #338: learner vocabulary and mistakes reach the tutor system prompt."""

import json
from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.models import Conversation, Lesson, LessonItem, LessonProgress, Message
from app.services.conversation_service import ConversationService
from app.services.learner_context import get_common_mistakes, get_learner_context, get_recent_vocab

CONTEXT_HEADER = "Your Student's Learning Context"


class _CapturingProvider:
    """Fake LLM provider that records the system prompt it receives."""

    def __init__(self) -> None:
        self.system_prompts: list[str] = []

    async def generate(self, messages, system_prompt="", **kwargs):
        self.system_prompts.append(system_prompt)
        return SimpleNamespace(content="Hola")


def _service(provider: _CapturingProvider) -> ConversationService:
    service = ConversationService(provider_name="mock")
    service._provider = provider
    return service


async def _add_user_message(db: AsyncSession, conversation_id: int, corrections: list | None):
    db.add(
        Message(
            conversation_id=conversation_id,
            role="user",
            content="hola",
            corrections=json.dumps(corrections) if corrections else None,
        )
    )
    await db.commit()


async def _new_conversation(db: AsyncSession, language: str = "spanish") -> Conversation:
    conversation = Conversation(language=language, difficulty_level="A1")
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@pytest.mark.asyncio
async def test_generate_response_puts_context_in_system_prompt():
    provider = _CapturingProvider()
    service = _service(provider)

    await service.generate_response(
        "Hola",
        "spanish",
        "A1",
        recent_vocab=["manzana", "casa"],
        common_mistakes=["Use 'estoy' for states"],
    )

    prompt = provider.system_prompts[-1]
    assert CONTEXT_HEADER in prompt
    assert "manzana" in prompt
    assert "Use 'estoy' for states" in prompt


@pytest.mark.asyncio
async def test_generate_response_without_history_has_no_context_section():
    provider = _CapturingProvider()
    await _service(provider).generate_response("Hola", "spanish", "A1")

    assert CONTEXT_HEADER not in provider.system_prompts[-1]


@pytest.mark.asyncio
async def test_common_mistakes_ranked_by_frequency_and_language_scoped(db: AsyncSession):
    es = await _new_conversation(db, "spanish")
    fr = await _new_conversation(db, "french")
    ser = {"original": "soy", "corrected": "estoy", "explanation": "Use estar for states"}
    gender = {"original": "el casa", "corrected": "la casa", "explanation": "casa is feminine"}
    await _add_user_message(db, es.id, [gender])
    await _add_user_message(db, es.id, [ser])
    await _add_user_message(db, es.id, [ser])
    await _add_user_message(db, es.id, None)
    await _add_user_message(db, fr.id, [{"explanation": "French only"}])

    mistakes = await get_common_mistakes(db, "Spanish")

    assert mistakes == ["Use estar for states", "casa is feminine"]


@pytest.mark.asyncio
async def test_common_mistakes_skips_bad_json_and_caps_at_five(db: AsyncSession):
    conv = await _new_conversation(db)
    db.add(Message(conversation_id=conv.id, role="user", content="x", corrections="{not json"))
    await db.commit()
    await _add_user_message(db, conv.id, [{"explanation": f"rule {i}"} for i in range(8)])

    assert len(await get_common_mistakes(db, "spanish")) == 5


@pytest.mark.asyncio
async def test_recent_vocab_needs_progress_for_language(db: AsyncSession):
    seen = Lesson(language="spanish", lesson_type="vocabulary", title="Fruit")
    unseen = Lesson(language="spanish", lesson_type="vocabulary", title="Animals")
    db.add_all([seen, unseen])
    await db.commit()
    db.add_all(
        [
            LessonItem(lesson_id=seen.id, item_type="word", content="manzana", order_index=0),
            LessonItem(lesson_id=seen.id, item_type="word", content="pera", order_index=1),
            LessonItem(lesson_id=unseen.id, item_type="word", content="perro", order_index=0),
            LessonProgress(lesson_id=seen.id, language="spanish", status="in_progress"),
        ]
    )
    await db.commit()

    assert await get_recent_vocab(db, "spanish") == ["manzana", "pera"]
    assert await get_recent_vocab(db, "french") == []


@pytest.mark.asyncio
async def test_learner_context_is_none_for_new_learner(db: AsyncSession):
    assert await get_learner_context(db, "spanish") == (None, None)


@pytest.mark.asyncio
async def test_chat_route_sends_learner_context_to_tutor(
    async_client: AsyncClient, db: AsyncSession, monkeypatch
):
    monkeypatch.setattr(settings, "correction_max_level", "0")  # skip the correction LLM call
    provider = _CapturingProvider()
    service = _service(provider)
    monkeypatch.setattr("app.routes.chat.get_conversation_service", lambda *a, **k: service)

    conv = await _new_conversation(db)
    await _add_user_message(
        db, conv.id, [{"original": "soy", "corrected": "estoy", "explanation": "Use estar"}]
    )

    response = await async_client.post(
        "/chat",
        json={
            "conversation_id": conv.id,
            "user_message": "Hola, estoy bien",
            "language": "spanish",
            "difficulty_level": "A1",
        },
    )

    assert response.status_code == 200, response.text
    prompt = provider.system_prompts[-1]
    assert CONTEXT_HEADER in prompt
    assert "Use estar" in prompt


@pytest.mark.asyncio
async def test_chat_route_without_history_keeps_plain_prompt(
    async_client: AsyncClient, db: AsyncSession, monkeypatch
):
    monkeypatch.setattr(settings, "correction_max_level", "0")
    provider = _CapturingProvider()
    service = _service(provider)
    monkeypatch.setattr("app.routes.chat.get_conversation_service", lambda *a, **k: service)

    conv = await _new_conversation(db)
    response = await async_client.post(
        "/chat",
        json={
            "conversation_id": conv.id,
            "user_message": "Hola",
            "language": "spanish",
            "difficulty_level": "A1",
        },
    )

    assert response.status_code == 200, response.text
    assert CONTEXT_HEADER not in provider.system_prompts[-1]
