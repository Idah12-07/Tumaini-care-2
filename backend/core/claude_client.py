"""
TUMAINI CARE — AI Companion Client (v3.0 — Hugging Face)
No IP blocking. No daily quota. Free forever.
"""
import os
import httpx
import asyncio
from core.prompts import GRIEF_COMPANION_PROMPT

# We use Mistral-7B-Instruct — excellent Swahili/English, free, no IP limits
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
HF_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def build_prompt(message: str, history: list) -> str:
    """Build Mistral instruction-format prompt."""
    prompt = f"<s>[INST] {GRIEF_COMPANION_PROMPT}\n\nBegin conversation. [/INST]"
    prompt += "Niko hapa nawe. I am here with you.</s>"

    # Add history (last 4 turns)
    found_user = False
    clean = []
    for turn in history[-4:]:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if not content or role not in ("user", "assistant"):
            continue
        if not found_user and role == "assistant":
            continue
        found_user = True
        clean.append((role, content))

    for role, content in clean:
        if role == "user":
            prompt += f"[INST] {content} [/INST]"
        else:
            prompt += f"{content}</s>"

    # Add current message
    prompt += f"[INST] {message} [/INST]"
    return prompt


async def get_companion_response(
    patient_id: str,
    message: str,
    language: str,
    history: list
) -> str:
    token = os.getenv("HF_API_TOKEN", "")

    if not token or token.startswith("your"):
        return (
            "[Tumaini offline — add HF_API_TOKEN to environment. "
            "Free token at huggingface.co/settings/tokens]"
        )

    prompt = build_prompt(message, history)

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    HF_URL,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 300,
                            "temperature": 0.7,
                            "return_full_text": False,
                            "stop": ["[INST]", "</s>"]
                        },
                        "options": {
                            "wait_for_model": True,
                            "use_cache": False
                        }
                    }
                )

                # Model loading — wait and retry
                if response.status_code == 503:
                    wait = 20 * (attempt + 1)
                    print(f"[Tumaini] Model loading, waiting {wait}s")
                    await asyncio.sleep(wait)
                    continue

                if response.status_code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"[Tumaini] Rate limited, waiting {wait}s")
                    await asyncio.sleep(wait)
                    continue

                if response.status_code != 200:
                    print(f"[Tumaini] HF error {response.status_code}: {response.text[:200]}")
                    return "Samahani, kuna tatizo dogo. / Sorry, a small error. Please try again."

                data = response.json()

                # Extract generated text
                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "").strip()
                elif isinstance(data, dict):
                    text = data.get("generated_text", "").strip()
                else:
                    text = ""

                if not text:
                    return "Samahani, jibu halikupatikana. / Sorry, no response received. Please try again."

                return text

        except httpx.TimeoutException:
            if attempt < 2:
                await asyncio.sleep(10)
                continue
            return "Samahani, muda umekwisha. / Sorry, request timed out. Please try again."
        except Exception as e:
            print(f"[Tumaini] Error: {type(e).__name__}: {e}")
            return "Samahani, kuna tatizo. / System error. Please try again."

    return "Samahani, jaribu tena baadaye. / Please try again in a moment."
