# syntax=docker/dockerfile:1

FROM python:3.9.17-bookworm
WORKDIR /
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]