FROM python:3.13-slim

RUN mkdir /output

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir uv
RUN uv pip install --no-cache-dir -r requirements.txt --system

COPY . .

ENV PYTHONPATH=.

ENTRYPOINT ["python", "main.py"]
