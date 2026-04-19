from __future__ import annotations

import copy
import inspect
from typing import Any, Callable, Dict


async def _call_maybe_async(fn: Callable, state: Dict[str, Any]) -> Dict[str, Any]:
    result = fn(state)
    if inspect.isawaitable(result):
        result = await result
    return result or {}


# ---- import your real agent entrypoints here ----
# Adjust ONLY these imports if your exported names differ.

from ai.agents.profile.node import profile_agent_node
from ai.agents.rag.agent import rag_agent
from ai.agents.readiness.agent import run_readiness_agent
from ai.agents.energy.agent import energy_agent
from ai.agents.learning.agent import learning_agent


def _readiness_patch_from_state(base: Dict[str, Any]) -> Dict[str, Any]:
    """run_readiness_agent mutates state; run on a copy and return merge patch only."""
    s = copy.deepcopy(base)
    run_readiness_agent(s)
    patch: Dict[str, Any] = {}
    if "readiness_signal" in s:
        patch["readiness_signal"] = s["readiness_signal"]
    ra = s.get("agent_runs", {})
    if "readiness_agent" in ra:
        patch["agent_runs"] = {"readiness_agent": ra["readiness_agent"]}
    bt = base.get("traces") or []
    st = s.get("traces") or []
    if len(st) > len(bt):
        patch["traces"] = st
    if s.get("errors"):
        patch["errors"] = s.get("errors", [])
    return patch


async def call_profile_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(profile_agent_node, state)


async def call_rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(rag_agent, state)


async def call_readiness_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return _readiness_patch_from_state(state)


async def call_energy_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(energy_agent, state)


async def call_learning_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    return await _call_maybe_async(learning_agent, state)
