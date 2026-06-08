"""
AI Service — abstraction layer supporting:
  - openai  → GPT-4o-mini (or any OpenAI model)
  - ollama  → Llama3, Mistral, DeepSeek, Gemma (local open-source)
  - mock    → static responses for dev/testing

To switch providers: set AI_PROVIDER in your .env file.
"""

from app.core.config import settings

# ── Mock responses (fallback / free tier) ─────────────────────────────────
MOCK_RESPONSES = {
    "restock": "📦 Based on your inventory, these products need restocking:\n• Products with quantity ≤ threshold are flagged.\nCheck your Inventory page for exact counts.",
    "top":     "🏆 Your top-selling product this month leads revenue. Check your Analytics page for the full breakdown.",
    "summary": "📊 Your business is performing well this week. Revenue is up vs last week based on recorded sales.",
    "predict": "🔮 Based on current stock velocity, 2–3 products may face shortages in the next 7 days. Restock soon.",
    "drop":    "📉 Sales drops often correlate with stockouts, public holidays, or competitor activity. Review your sales log.",
    "default": "I can help you analyze sales, inventory, and business performance. Try asking about your top products, revenue trends, or low stock alerts.",
}

def _mock_response(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["restock", "stock", "inventory"]): return MOCK_RESPONSES["restock"]
    if any(w in msg for w in ["top", "best", "most"]): return MOCK_RESPONSES["top"]
    if any(w in msg for w in ["summary", "week", "overview"]): return MOCK_RESPONSES["summary"]
    if any(w in msg for w in ["predict", "forecast", "shortage"]): return MOCK_RESPONSES["predict"]
    if any(w in msg for w in ["drop", "decline", "why"]): return MOCK_RESPONSES["drop"]
    return MOCK_RESPONSES["default"]

# ── OpenAI ─────────────────────────────────────────────────────────────────
async def _openai_response(message: str, context: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    system_prompt = f"""You are BizPulse AI, a business intelligence assistant for an African SME.
You have access to the following business data context:
{context}
Be concise, practical, and use Nigerian Naira (₦) for currency where relevant.
Format responses with bullet points and emojis for readability."""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ── Ollama (open-source local / self-hosted) ───────────────────────────────
async def _ollama_response(message: str, context: str) -> str:
    import httpx
    prompt = f"""You are BizPulse AI, a business assistant.
Business context: {context}
User question: {message}
Answer concisely with actionable insights."""

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
        )
        return response.json().get("response", "Unable to get AI response.")

# ── Main entry point ───────────────────────────────────────────────────────
async def get_ai_response(message: str, business_context: dict = None) -> tuple[str, str]:
    """
    Returns (reply_text, provider_name)
    business_context = dict with sales/inventory data to give AI real insight
    """
    context = ""
    if business_context:
        context = (
            f"Business: {business_context.get('business_name', 'N/A')}\n"
            f"Today's revenue: {business_context.get('today_revenue', 0)}\n"
            f"Monthly revenue: {business_context.get('monthly_revenue', 0)}\n"
            f"Total products: {business_context.get('total_products', 0)}\n"
            f"Low stock items: {business_context.get('low_stock', 0)}\n"
            f"Top products: {business_context.get('top_products', [])}"
        )

    provider = settings.AI_PROVIDER

    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            reply = await _openai_response(message, context)
            return reply, "openai"
        except Exception as e:
            # Fallback to mock if OpenAI fails
            return _mock_response(message) + f"\n\n_(OpenAI error: {str(e)[:60]})_", "mock"

    elif provider == "ollama":
        try:
            reply = await _ollama_response(message, context)
            return reply, "ollama"
        except Exception as e:
            return _mock_response(message) + f"\n\n_(Ollama error: {str(e)[:60]})_", "mock"

    else:
        return _mock_response(message), "mock"
