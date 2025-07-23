FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir uv
RUN uv pip install --no-cache-dir -r requirements.txt --system

COPY . .

# RUN pytest /app/tests

ENV PYTHONPATH=.

ENTRYPOINT ["python", "main.py"]