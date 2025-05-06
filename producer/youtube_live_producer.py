import requests
import json
import time
import os
import socket
from kafka import KafkaProducer

API_KEY = "AIzaSyBYthON0gEWiWKqO613QgrqLjXFqH_KHVA"
REGION = "IN"

def wait_for_kafka(host, port, timeout=60):
    print(f"Waiting for Kafka broker at {host}:{port}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("Kafka broker is available.")
                return
        except OSError:
            print("Kafka not ready, retrying...")
            time.sleep(2)
    raise Exception("Kafka broker not available after waiting")

# Wait for Kafka to be available
kafka_host, kafka_port = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092").split(":")
wait_for_kafka(kafka_host, int(kafka_port))

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=f"{kafka_host}:{kafka_port}",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_trending_videos():
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": REGION,
        "maxResults": 200,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json().get("items", [])

while True:
    print("Fetching trending videos...")
    for video in fetch_trending_videos():
        try:
            msg = {
                "video_id": video["id"],
                "title": video["snippet"]["title"],
                "channel_title": video["snippet"]["channelTitle"],
                "category_id": int(video["snippet"].get("categoryId", 0)),
                "publish_time": video["snippet"]["publishedAt"],
                "views": int(video["statistics"].get("viewCount", 0)),
                "likes": int(video["statistics"].get("likeCount", 0)),
                "dislikes": 0,
                "comment_count": int(video["statistics"].get("commentCount", 0)),
                "trending_date": time.strftime("%Y-%m-%d")
            }
            producer.send("youtube_trending", msg)
            print(f"Sent: {msg['title']}")
        except Exception as e:
            print("Error:", e)
    time.sleep(10) #TODO: less time for testing
