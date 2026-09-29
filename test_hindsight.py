"""
Step 2 test #2: confirm your Hindsight API key works.
Run this with:  python test_hindsight.py
You should see a saved memory get found again when you search for it.
"""

import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

BANK_ID = "sentinel-test-bank"  # "bank" = your project's memory space, name it anything

# Retain: save a test memory
client.retain(
    bank_id=BANK_ID,
    content="payment-service had 504 errors on Sept 14, fixed by scaling the DB connection pool",
)

# Recall: search for it
results = client.recall(bank_id=BANK_ID, query="payment-service errors")

print("Hindsight recall results:")
for r in results.results:
    print("-", r.text)