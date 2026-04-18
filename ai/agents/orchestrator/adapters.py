from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable, Dict


def _ensure_async(result: Any) -> Awaitable:
    async def _wrapper():
        return result
    return _wrapper()


async def _call_maybe_async(fn: Callable, state: Dict[str, Any]) -> Dict[str, Any]:
    result = fn(state)
    if inspect.isawaitable(result):
        result = await result
    return result or {}


# ---- import your real agent entrypoints here ----
# Adjust ONLY these imports if your exported names differ.

from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent
from ai.agents.readiness.agent import readiness_agent
from ai.agents.energy.agent import energy_agent
from ai.agents.learning.agent import learning_agent


async def call_profile_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(profile_agent_node, state)


async def call_rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(rag_agent, state)


async def call_readiness_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(readiness_agent, state)


async def call_energy_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(energy_agent, state)


async def call_learning_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(learning_agent, state)