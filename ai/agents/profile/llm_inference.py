from __future__ import annotations

import json
import os
from typing import Any, Dict, List
from dotenv import load_dotenv

from mistralai.client import Mistral
from ai.agents.profile.prompt import PROFILE_SYSTEM_PROMPT
from ai.agents.profile.schema import ProfileInference

load_dotenv()

def _serialize_history(history: List[Dict[str, Any]]) -> str:
    return json.dumps(history, ensure_ascii=False, indent=2)


def _serialize_dict(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def get_mistral_client() -> Mistral:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set")
    return Mistral(api_key=api_key)


async def infer_profile_with_mistral(
    *,
    query: str,
    history: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    signals: Dict[str, Any],
    model: str = "mistral-small-latest",
) -> ProfileInference:
    """
    Infer the student teaching profile using Mistral structured output.
    """

    client = get_mistral_client()

    user_message = f"""
Current user query:
{query}

Recent session history:
{_serialize_history(history)}

Explicit user profile:
{_serialize_dict(user_profile)}

Extracted behavioral signals:
{_serialize_dict(signals)}

Infer the best teaching-adaptation profile for this student right now.
Be conservative and only use evidence from the inputs.
""".strip()

    response = await client.chat.complete_async(
        model=model,
        messages=[
            {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "ProfileInference",
                "schema": ProfileInference.model_json_schema(),
            },
        },
        temperature=0.2,
        safe_prompt=False,
    )

    content = response.choices[0].message.content
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )

    data = json.loads(content)
    return ProfileInference.model_validate(data)