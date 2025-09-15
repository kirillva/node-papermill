FROM python:3.11.9-alpine3.20 AS build

RUN apk add build-base libpq libpq-dev python3-dev
RUN apk add gcc musl-dev linux-headers
RUN apk add libffi-dev

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

FROM python:3.11.9-alpine3.20 AS final

# Создание рабочей директории
WORKDIR /app

# Опционально: копирование ноутбуков по умолчанию
# COPY notebooks /notebooks

COPY ./ ./
COPY --from=build /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

VOLUME [ "/notebooks" ]

VOLUME [ "/files" ]

COPY app.py /app/app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]