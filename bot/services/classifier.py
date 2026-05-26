from openai import AsyncOpenAI
from bot.core.config import settings

CLASSIFY_PROMPT = '''
Determine the subject of this task in one word.
Reply with exactly one of: math / physics / chemistry / programming / russian / english / history / biology / other

Task: {text}

Reply (one word only):
'''

async def classify_subject(question: str) -> str:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": CLASSIFY_PROMPT.format(text=question)}
        ],
        max_tokens=10,
        temperature=0.0,
    )
    return response.choices[0].message.content.strip().lower()
