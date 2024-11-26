FROM python:3.12.3-slim

WORKDIR /app
COPY requieremnts.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
