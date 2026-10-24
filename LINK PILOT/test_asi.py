
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("ASI_ONE_API_KEY")

if not api_key:
    raise ValueError("ASI_ONE_API_KEY is missing from .env")

client = OpenAI(
    base_url="https://api.asi1.ai/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model="asi1",
    messages=[
        {"role": "user", "content": "Reply with exactly: LinkPilot connected!"}
    ],
)

print(response.choices[0].message.content)

