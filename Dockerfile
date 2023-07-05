# syntax=docker/dockerfile:1

FROM python:3.9.17-bookworm AS builder
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9.17-bookworm
WORKDIR /
COPY --from=builder / /
COPY . .
CMD ["python", "main.py"]
