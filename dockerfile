FROM python:3.11

# Встановлення робочої директорії
WORKDIR /app

# Копіюємо файли конфігурації
COPY pyproject.toml poetry.lock /app/
# Встановлення Poetry та залежностей
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копіюємо решту коду
COPY src /app/src
COPY main.py /app/main.py

# Відкриваємо порт
EXPOSE 8000

# Команда запуску
CMD ["poetry", "run", "python3", "main.py"]