# ai_agent.py service functions and data for ai agent router

import re 
import json
from groq import AsyncGroq
from config import settings

# Prompt for AI agent
PROMPT_ROLE="You`re an expert news analyst."
PROMPT_TOPICS="Your topic is {topic}."
PROMPT_DATA_INPUT="Your articles are {articles_json}."
PROMPT_TASK="You should filter out irrelevant articles. For each relevant one you should provide sentiment(positive/neutral/negative), summary and key events." 
PROMPT_OUTPUT="You should provide your answer in json without markdown, like this:"
PROMPT_EXAMPLE_OUTPUT="""
{{
  "relevant_articles": [
    {{
      "title": "...",
      "url": "...",
      "source": "...",
      "published_at": "...",
      "sentiment": "positive|neutral|negative"
    }}
  ],
  "summary": "...",
  "key_events": ["...", "..."]
}}
"""
ANALYSIS_PROMPT = f"{PROMPT_ROLE}\n{PROMPT_TOPICS}\n{PROMPT_DATA_INPUT}\n{PROMPT_TASK}\n{PROMPT_OUTPUT}\n{PROMPT_EXAMPLE_OUTPUT}"

# service function to add articles data into ai agent prompt
def _build_prompt(topic, articles):
    articles = articles[:10]
    articles_json = [
        {
            "title": article.get("title", ""),
            "description": (article.get("description") or "")[:300],
            "url": article.get("url", ""),
            "published_at": article.get("published_at", ""),
            "source": article.get("source", ""),
        }
        for article in articles
    ]
    return ANALYSIS_PROMPT.format(topic=topic, articles_json=articles_json)

# Service function to clean ai agent response and parse it into dict
def _parse_response(raw:str) -> dict:
# remove markdown code blocks if present
    cleaned = re.sub(r"```json|```", "", raw).strip()
    return json.loads(cleaned)

# Service function to call groq api with prompt and return response
async def _call_groq(prompt:str) -> str:
# Creating groq client
    client = AsyncGroq(api_key=settings.groq_api_key)

# Calling groq api with prompt
    response = await client.chat.completions.create(model=settings.groq_model,
                                                    messages=[{"role":"user", "content":f"{prompt}"}],
                                                    max_tokens=2048,
                                                    temperature=0.2)
    return response.choices[0].message.content

# Main service function to orchestrate process
async def analyze_articles(topic:str, articles:list, provider="groq"):
# Build prompt with articles data
    prompt = _build_prompt(topic, articles)
# Call ai provider with prompt and get raw response
    if provider == "groq":
        raw_response = await _call_groq(prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# Parse raw response into dict
    result_dict = _parse_response(raw_response)
# Set provider name in result dict
    provider_name = provider

    return (result_dict, provider_name)