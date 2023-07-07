# syntax=docker/dockerfile:1

FROM python:3.9.17-bookworm AS builder
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9.17-slim
WORKDIR /
COPY --from=builder . .
COPY main.py .
COPY logging_bot.py .
CMD ["python", "main.py"]
