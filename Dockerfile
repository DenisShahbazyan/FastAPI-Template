FROM python:3.12.3-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

RUN chmod +x /app/scripts/start_with_migration.sh /app/scripts/start.sh

ENTRYPOINT ["./scripts/start_with_migration.sh"]
