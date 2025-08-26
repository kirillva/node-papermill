FROM python:3.10.18-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание рабочей директории
WORKDIR /app

# Опционально: копирование ноутбуков по умолчанию
# COPY notebooks /notebooks

VOLUME [ "/notebooks" ]

VOLUME [ "/files" ]

COPY app.py /app/app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]