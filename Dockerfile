# ---- Base Python Slim ----
FROM python:3.11-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Install system dependencies (optional but useful) ----
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Copy only requirements first (for caching layers) ----
COPY requirements.txt .

# ---- Install Python dependencies ----
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- Copy full source code ----
COPY . .

# ---- Set envs ----
ENV PYTHONUNBUFFERED=1
ENV OPENROUTER_API_KEY=your_placeholder_key
ENV TELEGRAM_TOKEN=your_placeholder_token
ENV TELEGRAM_CHAT_ID=123456

# ---- Default run command ----
CMD ["python", "main.py"]
