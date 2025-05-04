FROM python:3.9-slim

WORKDIR /app

COPY youtube_live_producer.py .

RUN pip install kafka-python requests

CMD ["python", "youtube_live_producer.py"]
