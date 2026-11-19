from types import SimpleNamespace

import pytest

import src.maisaka.jargon_context_matcher as matcher
from src.plugin_runtime.capabilities.data import RuntimeDataCapabilityMixin
from src.services import memory_service as memory_module


@pytest.mark.asyncio
async def test_person_get_profile_returns_summary_and_traits(monkeypatch) -> None:
    calls = []

    async def get_person_profile(person_id, *, chat_id="", limit=10):
        calls.append((person_id, chat_id, limit))
        return SimpleNamespace(summary="常和麦麦聊 FF14", traits=["坦克玩家"])

    monkeypatch.setattr(memory_module.memory_service, "get_person_profile", get_person_profile)
    capability = RuntimeDataCapabilityMixin()
    result = await capability._cap_person_get_profile("p", "person.get_profile", {"person_id": "p1", "chat_id": "c1"})
    assert result == {"success": True, "summary": "常和麦麦聊 FF14", "traits": ["坦克玩家"]}
    assert calls == [("p1", "c1", 10)]
    assert (await capability._cap_person_get_profile("p", "person.get_profile", {}))["success"] is False


@pytest.mark.asyncio
async def test_jargon_match_only_looks_at_the_given_texts(monkeypatch) -> None:
    candidates = [
        matcher._JargonCandidate(content="高難", meaning="高难度副本", count=5, is_global=True, session_id_dict="{}"),
        matcher._JargonCandidate(content="T1", meaning="英雄联盟战队", count=9, is_global=True, session_id_dict="{}"),
    ]
    monkeypatch.setattr(matcher, "_load_scoped_jargon_candidates", lambda session_id: candidates)
    monkeypatch.setattr(matcher, "_load_high_frequency_terms", lambda session_id: {})
    capability = RuntimeDataCapabilityMixin()
    result = await capability._cap_jargon_match("p", "jargon.match", {"session_id": "s1", "texts": ["買房要打高難嗎"]})
    assert result == {"success": True, "jargons": [{"content": "高難", "meaning": "高难度副本"}]}
    assert (await capability._cap_jargon_match("p", "jargon.match", {"session_id": "s1"}))["success"] is False
