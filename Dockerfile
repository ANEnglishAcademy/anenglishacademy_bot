# Stable Python for aiogram/aiohttp
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (faster wheels & stable requests)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip and tools
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Optional: healthcheck for bot liveness
# HEALTHCHECK CMD curl --fail http://localhost:8080 || exit 1

# Optional: expose port if webhooks are used
# EXPOSE 8080

CMD ["python", "bot.py"]
