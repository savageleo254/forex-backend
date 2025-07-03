import os
import logging
import requests
from dotenv import load_dotenv

# 1️⃣ ProVeteran+++ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# 2️⃣ ProVeteran+++ Load OpenRouter API key from .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key or not api_key.startswith("sk-or-"):
    logging.critical("OPENROUTER_API_KEY missing or invalid in .env! Exiting.")
    exit(1)
logging.info(f"OpenRouter API key loaded and set (ending with ...{api_key[-4:]})")

# 3️⃣ ProVeteran+++ Prepare secure request
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/savageleo254/forex-backend",  # Update if public repo/app URL changes
    "X-Title": "Forex Backend ProVeteran+++ Script"
}
payload = {
    "model": "deepseek/deepseek-chat-v3-0324:free",  # Correct OpenRouter model name
    "messages": [
        {"role": "user", "content": "Say hello to the world in French."}
    ]
}

# 4️⃣ ProVeteran+++ Make the request and handle errors robustly
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    logging.info(f"HTTP Request: POST {url} Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        reply = data['choices'][0]['message']['content'].strip()
        print("OpenRouter/DeepSeek response:", reply)
    elif response.status_code == 401:
        logging.error("Authentication failed: Invalid OpenRouter API key.")
        print("Check your API key and OpenRouter account status.")
    else:
        logging.error(f"OpenRouter API call failed: {response.status_code} {response.text}")
        print(f"OpenRouter API call failed: {response.status_code} {response.text}")
except Exception as e:
    logging.error(f"Exception during OpenRouter API call: {e}")
    print("Error contacting OpenRouter API:", e)