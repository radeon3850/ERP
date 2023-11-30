# Використовуємо базовий образ з підтримкою Python
FROM python:3.9

# Створюємо робочий каталог в контейнері
WORKDIR /app

# Копіюємо файли додатку в контейнер
COPY . /app

# Встановлюємо залежності
RUN pip install -r requirements.txt
RUN pip install python-dotenv

# Добавляємо змінну середовища для
ENV SECRET_KEY=436c119d80be340f663a0a11009dda10f3a2bbd6
ENV FLASK_DEBUG=FALSE
ENV SECRET_KEY=436c119d80be340f663a0a11009dda10f3a2bbd6
ENV FLASK_APP=erp.py

# Встановлюємо Gunicorn
RUN pip install gunicorn

# Вказуємо команду для запуску додатку з використанням Gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--timeout", "120", "--workers", "3", "--threads", "3", "--worker-connections", "1000"]

EXPOSE 8000
