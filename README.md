# Sentinel — Incident Response Agent with a Living Runbook

Built for HackwithHyderabad 3.0, using Hindsight (Vectorize) for persistent
agent memory.

## What it does
An on-call assistant that remembers past incidents and how they were fixed.
Over time it also reflects across incidents to auto-update a runbook
document with newly discovered patterns.

## Setup
1. `python -m venv venv` then activate it
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and paste in your real Groq + Hindsight API keys
4. `python test_groq.py` — should print a short LLM response
5. `python test_hindsight.py` — should print back a saved memory

## How Hindsight memory is used
(Fill this in as you build — this section doubles as your submission's
required "Explanation of how Hindsight memory is used".)