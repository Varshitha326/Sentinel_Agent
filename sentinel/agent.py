"""
Sentinel agent core.
All three core functions are now built:
save_incident() -> ask_agent() -> reflect_and_update_runbook()
"""

import os
import asyncio
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv()

BANK_ID = "sentinel-incidents"
RUNBOOK_PATH = "runbook.md"  # the "living document" that grows over time

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _get_hindsight_client() -> Hindsight:
    """Create a fresh Hindsight client for this call only.
    Avoids reusing a client tied to a stale/different asyncio event loop,
    which is what breaks under Streamlit's rerun model."""
    return Hindsight(
        base_url=os.getenv("HINDSIGHT_BASE_URL"),
        api_key=os.getenv("HINDSIGHT_API_KEY"),
    )


def _run(coro):
    """Run an async call in a fresh event loop that's properly closed
    afterward, instead of relying on the SDK's own sync wrapper."""
    return asyncio.run(coro)


def save_incident(description: str) -> None:
    """Store a past incident + its resolution into Hindsight (Retain)."""
    client = _get_hindsight_client()
    _run(client.aretain(bank_id=BANK_ID, content=description))

def ask_agent(new_problem: str) -> str:
    """Recall similar past incidents, ask the LLM for a plain-English fix."""
    client = _get_hindsight_client()
    recall_results = client.recall(bank_id=BANK_ID, query=new_problem)
    past_incidents = [r.text for r in recall_results.results]

    if past_incidents:
        context = "Past incidents from memory (may or may not be relevant):\n"
        context += "\n".join(f"- {incident}" for incident in past_incidents)
    else:
        context = "No similar past incidents were found in memory."

    prompt = f"""You are a friendly assistant that helps a team fix technical
problems. The person reading your answer may NOT be technical (for example a
manager, a support agent, or a new team member). Write in simple, plain English.

Problem reported:
"{new_problem}"

{context}

Rules:
- Avoid jargon. If you must use a technical term, explain it in a few words
  in brackets.
- Only cite a past incident if it has the SAME kind of symptom as the reported
  problem. Sharing a service name or a word like "login" is NOT enough.
- When you cite a past incident, describe it exactly as it appears above.
  Never add symptoms, causes or details that are not in the memory text.
- If no past incident clearly matches, begin "Why we think so" with:
  "No close match in memory, so this is a general suggestion." and do not
  mention any dates.
- Never invent past incidents.
- If a past incident is only loosely related, say "possibly related" and never state a guessed cause as if it were certain.
- Use EXACTLY this format, and keep it short:

**What's probably wrong:** one simple sentence.

**What to do:**
1. first step
2. second step
3. third step (only if needed)

**Why we think so:** one or two sentences."""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def reflect_and_update_runbook() -> str:
    """
    Ask Hindsight to reflect across ALL stored incidents, find recurring
    patterns, and turn that insight into an updated runbook document.
    Returns the new runbook content (also writes it to runbook.md).
    """
    client = _get_hindsight_client()

    # 1. Ask Hindsight to reflect - this looks across everything in the bank
    #    and synthesizes an answer, not just a search result.
    reflection = _run(client.areflect(
        bank_id=BANK_ID,
        query=(
            "Looking across all stored incidents, what recurring root causes "
            "or patterns show up more than once? For each pattern found, name "
            "the root cause, list which services/incidents it appeared in, "
            "and give a one-line recommended action."
        ),
    ))
    insight_text = reflection.text

    # 2. Turn that insight into a runbook section
    runbook_prompt = f"""Turn this incident analysis into a short, well-formatted
markdown runbook section with a heading and bullet points. Keep it concise
and scannable for an on-call engineer under pressure.

Use plain Markdown only - do not use any HTML tags like <br>. For any
multi-step action, write it as a numbered Markdown list, one step per
line, like:
1. First step
2. Second step
3. Third step

{insight_text}"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": runbook_prompt}],
    )
    new_section = response.choices[0].message.content

    # 3. Write/overwrite the runbook file with the fresh content
    runbook_content = f"""# Sentinel Runbook
*Auto-generated from incident memory. Last updated by Reflect.*

{new_section}
"""
    with open(RUNBOOK_PATH, "w", encoding="utf-8") as f:
        f.write(runbook_content)

    return runbook_content
def list_memory_items(limit: int = 100):
    """Return (total, list_of_text) of what is stored in the Hindsight bank."""
    client = _get_hindsight_client()
    result = client.list_memories(bank_id=BANK_ID, limit=limit, offset=0)
    texts = []
    for item in result.items:
        if isinstance(item, dict):
            text = item.get("text") or item.get("content") or str(item)
        else:
            text = getattr(item, "text", None) or getattr(item, "content", None) or str(item)
        texts.append(text)
    total = getattr(result, "total", len(texts))
    return total, texts