import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from supabase_client import supabase

# 🔥 dotenv 로드 (가장 위에서)
load_dotenv()

BROKER = os.getenv("MQTT_HOST")
PORT = 8883
USERNAME = os.getenv("MQTT_USERNAME")
PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC = "sensor/#"

if not all([BROKER, USERNAME, PASSWORD]):
    raise RuntimeError("❌ MQTT 환경변수가 설정되지 않았습니다.")

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

def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_start()