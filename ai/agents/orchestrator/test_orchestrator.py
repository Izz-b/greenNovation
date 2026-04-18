import asyncio

from ai.agents.orchestrator.graph import graph
from ai.agents.orchestrator.context_builder import build_initial_context


async def main():
    context = build_initial_context(
        query="Explain recursion with simple examples because I have an exam tomorrow",
        user_profile={
            "user_id": "u1",
            "preferred_language": "en",
            "academic_level": "undergraduate",
            "department": "software engineering",
        },
        session_history=[
            {"role": "user", "content": "I get confused with recursion"},
            {"role": "user", "content": "Please explain step by step"},
        ],
    )

    result = await graph.ainvoke(context)

    print("\nROUTING:\n", result.get("routing"))
    print("\nMERGED SIGNAL BUNDLE:\n", result.get("merged_signal_bundle"))
    print("\nFINAL RESPONSE:\n", result.get("final_response"))
    print("\nAGENT RUNS:\n", result.get("agent_runs"))
    print("\nWARNINGS:\n", result.get("warnings"))


if __name__ == "__main__":
    asyncio.run(main())