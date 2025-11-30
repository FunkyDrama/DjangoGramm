FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY assets/package*.json ./assets/

WORKDIR /app/assets
RUN npm ci

WORKDIR /app
COPY . .

WORKDIR /app/assets
RUN npm run build

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_BUILD=true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-root --only main

COPY . .

COPY --from=frontend-builder /app/static/dist/ ./static/dist/

RUN python manage.py collectstatic --noinput --clear

RUN curl -sSLo /usr/local/bin/wait-for-it \
    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
 && chmod +x /usr/local/bin/wait-for-it

EXPOSE 8000

ENV DOCKER_BUILD=false

CMD ["wait-for-it", "db:5432", "--", "sh", "-c", \
     "python manage.py migrate --noinput && \
      gunicorn djangogramm.wsgi:application --bind 0.0.0.0:8000 --workers 3"]