FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg (Postgres driver) and bcrypt build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Run migrations then start the server. In production, split these into
# separate steps (a release/migrate job + a stateless web process) --
# combined here for local docker-compose simplicity.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
