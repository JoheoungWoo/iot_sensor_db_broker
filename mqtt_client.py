import json
import os
import time
import random
import threading
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from supabase_client import supabase

# 🔥 dotenv 로드
load_dotenv()

BROKER = os.getenv("MQTT_HOST")
PORT = 8883
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC = "JoHeoungWoo"

if not all([BROKER, USERNAME, PASSWORD]):
    raise RuntimeError("❌ MQTT 환경변수가 설정되지 않았습니다.")

# -----------------------
# MQTT SUBSCRIBER
# -----------------------
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT Connected:", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="ignore")
    print("📩 RX:", msg.topic, payload)

    try:
        supabase.table("sensor_data").insert({
            "device_id": msg.topic.split("/")[1],
            "topic": msg.topic,
            "payload": json.loads(payload)
        }).execute()
    except Exception as e:
        print("❌ Supabase insert error:", e)

# -----------------------
# DUMMY PUBLISHER
# -----------------------
def start_dummy_publisher():
    pub = mqtt.Client()
    pub.username_pw_set(USERNAME, PASSWORD)
    pub.tls_set()
    pub.connect(BROKER, PORT)

    while True:
        data = {
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(40, 60), 2),
            "gx": round(random.uniform(-1, 1), 3),
            "gy": round(random.uniform(-1, 1), 3),
            "gz": round(random.uniform(-1, 1), 3),
        }

        topic = "sensor/dummy01/data"
        pub.publish(topic, json.dumps(data))
        print("🧪 Dummy published:", data)

        time.sleep(1)

# -----------------------
# START MQTT
# -----------------------
def start_mqtt():
    # subscriber
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_start()

    # 🔥 dummy publisher는 별도 thread
    threading.Thread(
        target=start_dummy_publisher,
        daemon=True
    ).start()
