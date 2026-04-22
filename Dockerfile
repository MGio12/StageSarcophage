FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    smbclient \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/modes-degrades /app/instance /app/logs

ENV FLASK_ENV=production
ENV STORAGE_DIR=/data/modes-degrades

EXPOSE 5000

CMD ["python", "run.py"]
