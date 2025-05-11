FROM python:3.10.12-slim

# Установка Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

# Установка рабочей директории
WORKDIR /app

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock* /app/

# Установка зависимостей через poetry без создания виртуального окружения
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем весь проект
COPY . .

# Установка разрешений на запуск entrypoint
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=QuartzAgency.settings \
    PYTHONPATH=/app

ENTRYPOINT ["/app/entrypoint.sh"]
