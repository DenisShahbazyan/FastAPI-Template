FROM python:3.14.3-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y postgresql-client \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Сначала зависимости — слой кешируется пока lock-файл не меняется
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .

EXPOSE 8000

RUN chmod +x /app/scripts/start_with_migration.sh /app/scripts/start.sh

# Создаём непривилегированного пользователя
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home appuser \
    && chown -R appuser:appgroup /app

# Помещаем скрипты в PATH, чтобы их можно было запускать без uv run
ENV PATH="/app/.venv/bin:$PATH"

USER appuser:appgroup

ENTRYPOINT ["./scripts/start_with_migration.sh"]
