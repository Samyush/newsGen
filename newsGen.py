!pip install groq news-google-api newsapi-python python-dotenv requests

import os
import requests
import streamlit as st
from newsapi import NewsApiClient

# Load API keys

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
hf_token = st.secrets["HF_TOKEN"]
openai_key = st.secrets["OPENAI_API_KEY"]
NEWSAPI_KEY = st.secrets["NEWSAPI_KEY"]


if not GROQ_API_KEY or not NEWSAPI_KEY:
    st.error("Missing GROQ_API_KEY or NEWSAPI_KEY in environment.")
    st.stop()

# Initialize clients
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Get news
def get_top_headlines(limit=10):
    response = newsapi.get_top_headlines(language='en', page_size=limit)
    return response.get("articles", [])[:limit]

# Paraphrasing
def paraphrase_with_groq(title, description):
    if not title:
        return "⚠️ Skipped: No title."

    if not description:
        description = "No description provided."

    input_text = f"{title}. {description}"

    prompt = f"""
Paraphrase the following news content in a publish-ready, professional, and neutral tone.
- Keep it concise (4–8 sentences).
- Do not copy phrases or include links.

Article:
\"\"\"{input_text}\"\"\"
    """

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt.strip()}],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=GROQ_HEADERS, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="AI News Summarizer", layout="wide")
st.title("📰 AI-Powered Top News Paraphraser")
# st.caption("Powered by NewsAPI + GROQ LLM")
st.caption("samyush")

limit = st.slider("How many top news items to fetch?", 1, 15, 10)

if st.button("Generate News"):
    with st.spinner("Fetching and paraphrasing news..."):
        articles = get_top_headlines(limit)
        for i, article in enumerate(articles):
            title = (article.get("title") or "").strip()
            description = (article.get("description") or "").strip()
            url = (article.get("url") or "").strip()
            source = article.get("source", {}).get("name", "Unknown Source")
            published_at = article.get("publishedAt", "Unknown Date")

            paraphrased = paraphrase_with_groq(title, description)

            st.markdown(f"### {i+1}. {paraphrased}")
            st.markdown(f"**Source**: [{source}]({url})")
            st.markdown(f"**Published**: {published_at}")
            st.markdown("---")
