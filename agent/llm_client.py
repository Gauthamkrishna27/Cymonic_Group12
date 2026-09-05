"""
llm_client.py — Sub-member A

Sends the built prompt to Gemini over HTTPS and parses the JSON response
back into a Python dict. Raises LLMCallError on any failure so
reasoning.py can catch it and fall back to Sub-member B's rule engine.
"""

import os
import json
import requests

from prompts import build_prompt

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

# Keep the request tight — we don't need a long response, just one JSON object
REQUEST_TIMEOUT_SECONDS = 8


class LLMCallError(Exception):
    """Raised whenever the LLM path can't be trusted to produce a result —
    network failure, bad status code, or a response that isn't valid JSON
    in the expected shape. reasoning.py catches this and calls the
    fallback instead."""
    pass


def call_llm(context: dict) -> dict:
    """
    Takes the context dict, builds the prompt, calls Gemini, and returns
    a dict with keys: decision, reasoning, offer.

    Raises LLMCallError if anything goes wrong, so the caller can fall
    back to fallback_rules.fallback_score() without crashing the app.
    """
    if not GEMINI_API_KEY:
        raise LLMCallError("Missing GEMINI_API_KEY environment variable")

    prompt = build_prompt(context)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,       # low temperature — we want consistent judgment, not creativity
            "response_mime_type": "application/json",
        },
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as e:
        raise LLMCallError(f"Network error calling Gemini: {e}") from e

    if response.status_code != 200:
        raise LLMCallError(
            f"Gemini returned status {response.status_code}: {response.text[:200]}"
        )

    try:
        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError) as e:
        raise LLMCallError(f"Unexpected Gemini response shape: {e}") from e

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise LLMCallError(f"Gemini response wasn't valid JSON: {e}") from e

    for key in ("decision", "reasoning", "offer"):
        if key not in result:
            raise LLMCallError(f"Gemini response missing required key: {key}")

    return result
