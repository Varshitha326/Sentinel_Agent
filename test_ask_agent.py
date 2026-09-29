"""
Step 4 test: try asking the agent about a new problem similar to something
already in memory, and something unrelated.
Run with: python test_ask_agent.py
"""

from sentinel.agent import ask_agent

print("=== Test 1: similar to a saved incident (DB pool exhaustion pattern) ===")
answer1 = ask_agent("checkout-service is throwing 504 errors under load, response times climbing")
print(answer1)

print("\n=== Test 2: something unrelated to anything saved ===")
answer2 = ask_agent("users are reporting the mobile app crashes on startup after the latest update")
print(answer2)