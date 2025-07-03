import os
import asyncio
import signal
import feedparser
import hashlib
import json
import openai
import logging
import os
import json
import logging
import openai
import jsonschema

from typing import List
import redis.asyncio as aioredis

# ─── CONFIG ────────────────────────────────────────────────────────────────
RSS_URLS = [
    "https://www.forexfactory.com/ffnews.xml",
    # add more RSS or JSON endpoints here
]
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CACHE_TTL = 300             # seconds
POLL_INTERVAL = 60          # seconds between loops
FAIL_THRESHOLD = 3          # consecutive errors before cooling off
COOLDOWN_SECONDS = 300      # how long to pause when tripped (5 min)

openai.api_key = OPENAI_API_KEY

# ─── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# ─── CIRCUIT BREAKER & SHUTDOWN ──────────────────────────────────────────────
fail_count = 0
stop_event = asyncio.Event()

def _signal_handler():
    logging.info("Shutdown signal received.")
    stop_event.set()

signal.signal(signal.SIGINT, lambda *_: _signal_handler())
signal.signal(signal.SIGTERM, lambda *_: _signal_handler())

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

async def get_redis():
    return aioredis.from_url(REDIS_URL, decode_responses=True)

def fetch_news() -> List[str]:
    headlines = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            headlines.append(entry.title)
    return headlines

async def parse_sentiment(text: str):
    prompt = (
        f"Analyze this news headline and output JSON:\n\n"
        f"Headline: \"{text}\"\n\n"
        "{\n"
        '  "directional_bias": float,  # -1 to +1\n'
        '  "tone": "hawkish|dovish|neutral",\n'
        '  "urgency": "high|medium|low"\n'
        "}"
    )
    res = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional forex analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=100
    )
    try:
        return json.loads(res.choices[0].message.content)
    except json.JSONDecodeError:
        logging.warning("LLM response not valid JSON; defaulting neutral sentiment")
        return {"directional_bias": 0.0, "tone": "neutral", "urgency": "low"}

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
async def news_loop():
    global fail_count
    redis_client = await get_redis()

    while not stop_event.is_set():
        try:
            headlines = fetch_news()
            if not headlines:
                logging.warning("No headlines fetched")
            sentiments = await get_sentiments(headlines, redis_client)
            payload = [{"headline": h, **s} for h, s in zip(headlines, sentiments)]

            await redis_client.set("latest_news_sentiments", json.dumps(payload), ex=CACHE_TTL)
            logging.info(f"Processed {len(payload)} news items")
            fail_count = 0

        except Exception as e:
            fail_count += 1
            logging.error(f"news_loop error #{fail_count}: {e}", exc_info=True)
            if fail_count >= FAIL_THRESHOLD:
                logging.warning(f"Circuit breaker tripped: cooling down for {COOLDOWN_SECONDS}s")
                await asyncio.sleep(COOLDOWN_SECONDS)
                fail_count = 0

        # wait either until next poll or shutdown signal
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL)
        except asyncio.TimeoutError:
            continue

    logging.info("Exiting news_loop cleanly.")

async def get_sentiments(headlines: List[str], redis_client) -> List[dict]:
    results = [None] * len(headlines)
    uncached = []
    indices = []

    # 1️⃣ Check cache
    for i, h in enumerate(headlines):
        key = f"news:{hash_text(h)}"
        cached = await redis_client.get(key)
        if cached:
            results[i] = json.loads(cached)
        else:
            uncached.append(h)
            indices.append(i)

    # 2️⃣ Batch process uncached (simple batching stub)
    BATCH_SIZE = 5
    for i in range(0, len(uncached), BATCH_SIZE):
        batch = uncached[i:i+BATCH_SIZE]
        # here you could build a combined prompt for the batch
        # for now, call parse_sentiment individually:
        tasks = [parse_sentiment(txt) for txt in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        for j, res in enumerate(batch_results):
            idx = indices[i+j]
            sentiment = res if isinstance(res, dict) else {"directional_bias": 0.0, "tone": "neutral", "urgency": "low"}
            results[idx] = sentiment
            await redis_client.set(f"news:{hash_text(batch[j])}", json.dumps(sentiment), ex=CACHE_TTL)

    return results

# ─── ENTRYPOINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.info("Starting news_feed service...")
    asyncio.run(news_loop())
    logging.info("news_feed service stopped.")
