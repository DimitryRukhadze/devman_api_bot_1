# syntax=docker/dockerfile:1

FROM python:3.9.17-slim
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
COPY logging_bot.py .
CMD ["python", "main.py"]
