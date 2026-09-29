"""
Step 3: generate realistic fake past incidents and save them into Hindsight.
Run this with:  python generate_incidents.py
Only needs to be run ONCE from terminal (or again if you want fresh/more data).
Also importable by app.py, which reuses PROMPT and generate_and_save().
"""

import os
from dotenv import load_dotenv
from groq import Groq
from sentinel.agent import save_incident

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PROMPT = """Generate 12 realistic but fictional software incident reports for a
tech company. Each one should be 2-3 sentences: what broke, the error/symptom,
and how it was fixed. Use realistic service names (e.g. payment-service,
auth-service, checkout-api, notifications-worker) and realistic-sounding dates
in September 2026.

IMPORTANT: Make exactly 3 of these incidents secretly share the same root
cause - database connection pool exhaustion - but on DIFFERENT services and
with DIFFERENT surface symptoms (timeouts, 504s, slow queries), so the
pattern isn't obvious just from reading one. Also include 2 incidents that
were fixed by a service restart, 2 caused by a bad deploy, and the rest can
be varied (memory leak, expired cert, rate limiting, etc).

Output ONLY a numbered list, one incident per line, nothing else."""


def generate_and_save():
    """Generate incidents and save them. Returns the list of incident strings."""
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": PROMPT}],
    )
    raw_text = response.choices[0].message.content

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    incidents = []
    for line in lines:
        parts = line.split(". ", 1)
        text = parts[1] if len(parts) == 2 and parts[0].isdigit() else line
        incidents.append(text)

    for incident in incidents:
        save_incident(incident)

    return incidents


# Only runs when you execute this file directly (python generate_incidents.py),
# NOT when app.py imports PROMPT/generate_and_save from it.
if __name__ == "__main__":
    print("Generating incidents...\n")
    incidents = generate_and_save()
    print(f"Saved {len(incidents)} incidents:\n")
    for i in incidents:
        print("-", i)