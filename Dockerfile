FROM python:3.9-slim-buster

EXPOSE 80

WORKDIR /app

ARG TELEGRAMBOT_TOKEN
ENV TELEGRAMBOT_TOKEN=$TELEGRAMBOT_TOKEN

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "telegram.py"]

COPY . .
