FROM python:3.12-slim

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Исходный код
COPY . .

# Создать директории для статики, медиа, логов
RUN mkdir -p staticfiles media logs && touch logs/realty.log

# Переменные среды
ENV DJANGO_SETTINGS_MODULE=realty_agency.settings
ENV PYTHONUNBUFFERED=1

# Собрать статику и применить миграции при запуске
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && \
                  python manage.py collectstatic --noinput && \
                  python manage.py seed_data && \
                  python manage.py runserver 0.0.0.0:8000"]
