
from openai import AsyncOpenAI
import base64
from bot.core.config import settings
from bot.services.limiter import reserve_cost, adjust_cost
from bot.services.classifier import classify_subject

SYSTEM_PROMPT = '''
You are a knowledgeable tutor helping a student understand how to solve a problem.
Your goal is to explain the solution clearly, not just give the answer.
Always respond in Russian.

The student studies in: {country}. Adapt your explanation, notation, and terminology to match the standard educational curriculum of this country.

Response format (always follow this structure):

**Что дано:**
[briefly restate what is given]

**Метод:**
[which method/formula/approach and WHY this one]

**Решение:**
[step-by-step, each step numbered, each step explained in plain language]

**Ответ:**
[final answer, clearly highlighted]

**Проверка:**
[how to verify the answer is correct — skip if not applicable]

Rules:
- Write like a good teacher explains at the board
- Use examples if the concept is complex
- If the problem is unclear or incomplete, ask one clarifying question
- Never add unnecessary filler text
- Keep math formulas readable (use Unicode symbols: ², √, π, ≤, ≥, ±)
- For programming tasks: always include working code with comments
- If you genuinely cannot solve the task, say so honestly

Subject context: {subject}
'''

async def solve_task(question: str, country: str, file_path: str = None) -> tuple[str, str, int, float]:
    estimated_cost = 0.03
    if not await reserve_cost(estimated_cost):
        return "Сервис временно недоступен, попробуй позже", "other", 0, 0.0

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    subject = await classify_subject(question)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(country=country, subject=subject)}
    ]
    model = "gpt-4o"
    content = []
    if file_path:
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        content.append({"type": "text", "text": question})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
    else:
        model = "gpt-4o-mini"
        content.append({"type": "text", "text": question})

    messages.append({"role": "user", "content": content})

    try:
        response = await client.chat.completions.create(model=model, messages=messages, max_tokens=2000)
        answer = response.choices[0].message.content
        usage = response.usage
        
        # Simplified cost calculation
        cost = (usage.prompt_tokens * 0.000005) + (usage.completion_tokens * 0.000015) # gpt-4o pricing
        
        await adjust_cost(cost, estimated_cost)
        return answer, subject, usage.total_tokens, cost
    except Exception as e:
        await adjust_cost(0, estimated_cost)
        print(f"Error in solver: {e}")
        return "Извините, произошла ошибка при обработке вашего запроса.", "error", 0, 0.0
