"""
Step 5 test: run Reflect and see the runbook get built.
Run with: python test_reflect.py
Then open runbook.md to see the actual file it created.
"""

from sentinel.agent import reflect_and_update_runbook

print("Running Reflect... (this may take a few seconds)\n")
runbook = reflect_and_update_runbook()

print("=== New runbook content ===\n")
print(runbook)
print("\n(Also saved to runbook.md in this folder)")