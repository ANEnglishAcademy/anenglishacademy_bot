# 1) Stable Python that works with aiogram/aiohttp
FROM python:3.11-slim

# 2) Make pip quiet about root *during build*
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

# 3) OS deps (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gcc \
 && rm -rf /var/lib/apt/lists/*

# 4) Create non-root user to run the app (security + no warnings at runtime)
RUN useradd -m appuser

# 5) Set workdir and copy only requirements first (better caching)
WORKDIR /app
COPY requirements.txt ./

# 6) Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 7) Copy the rest of the project, give ownership to non-root
COPY . .
RUN chown -R appuser:appuser /app

# 8) Drop privileges
USER appuser

# 9) Start the bot (aiogram long-polling)
CMD ["python", "bot.py"]
