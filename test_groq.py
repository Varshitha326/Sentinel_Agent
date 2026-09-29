"""
Step 2 test #1: confirm your Groq API key works.
Run this with:  python test_groq.py
You should see a short text answer printed below.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # reads the .env file and loads GROQ_API_KEY into memory

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "In one sentence, what causes a 504 error?"}
    ],
)

print("Groq responded:")
print(response.choices[0].message.content)