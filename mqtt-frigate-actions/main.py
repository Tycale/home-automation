#!/usr/bin/env python3
import json
import os
import paho.mqtt.client as mqtt
import threading

PORT = int(get_env_var('MQTT_PORT', default='1883'))
BROKER = get_env_var('MQTT_IP')
CLIENT_ID = get_env_var('MQTT_CLIENT')
USERNAME = get_env_var('MQTT_USER')
PASSWORD = get_env_var('MQTT_PASS')

# Topics MQTT
DAYTIME_TOPIC = get_env_var('MQTT_TOPIC_DAYTIME')
FRIGATE_EVENTS_TOPIC = "frigate/events"
GARAGE_LEDS_TOPIC = "command/ledgarage/light"
ABRIS_LEDS_TOPIC1 = "cmnd/esp-ledsjardin/POWER4"
ABRIS_LEDS_TOPIC2 = "cmnd/esp-ledsjardin/POWER5"
HUGO_TOPIC1 = "cmnd/esp-terrasse/POWER3"
HUGO_TOPIC2 = "cmnd/esp-terrasse/POWER5"
PODO_TOPIC1 = "cmnd/esp-terrasse/POWER6"
PODO_TOPIC2 = "cmnd/esp-terrasse/POWER4"

# Global variables
common_topics = [HUGO_TOPIC1, HUGO_TOPIC2, PODO_TOPIC1, PODO_TOPIC2]
score_threshold = 0.76
event_counter = {}
off_timers = {}
is_night = False

# Initialize event_counter and off_timers for each topic
for topic in common_topics + [GARAGE_LEDS_TOPIC, ABRIS_LEDS_TOPIC1, ABRIS_LEDS_TOPIC2]:
    event_counter[topic] = 0
    off_timers[topic] = None

def get_env_var(name, default=None):
    var = os.getenv(name, default)
    if var is None:
        sys.exit(f"Error: {name} is not set")
    return var

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(FRIGATE_EVENTS_TOPIC)
    client.subscribe(DAYTIME_TOPIC)

def on_message(client, userdata, msg):
    global is_night
    print(f"Received message: {msg.topic} {str(msg.payload)}")

    if msg.topic == DAYTIME_TOPIC:
        is_night = str(msg.payload) == "night"
        return

    # Convert message to JSON
    data = json.loads(msg.payload)

    # Check if the event is related to a "person"
    if data["before"]["label"] == "person":
        if data["before"]["camera"] == "garage":
            handle_camera_event(client, data, GARAGE_LEDS_TOPIC)
        elif data["before"]["camera"] == "abris":
            handle_camera_event(client, data, ABRIS_LEDS_TOPIC1, ABRIS_LEDS_TOPIC2)

def handle_camera_event(client, data, *camera_topics):
    global is_night

    if not is_night:
        return

    topics = list(camera_topics) + common_topics
    if (data["type"] == "new" or data["type"] == "update") and float(data["before"]["top_score"]) > score_threshold or float(data["after"]["score"]) > score_threshold:
        # Increase the counter for each topic
        for topic in topics:
            event_counter[topic] += 1

            # Cancel previous timer if it exists
            if off_timers[topic]:
                off_timers[topic].cancel()
                off_timers[topic] = None

            # Turn on the light
            client.publish(topic, "ON")
            print(f"Turned ON light for topic: {topic}")
    elif data["type"] == "end":
        # Decrease the counter for each topic
        for topic in topics:
            event_counter[topic] -= 1

            # Set timer to turn off light after 2 minutes if no events are active
            if event_counter[topic] == 0 and not off_timers[topic]:
                off_timers[topic] = threading.Timer(120, turn_off_light, args=(client, topic))
                off_timers[topic].start()

def turn_off_light(client, topic):
    client.publish(topic, "OFF")
    print(f"Turned OFF light for topic: {topic}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection with result code {rc}")

def main():
    client = mqtt.Client(client_id=CLIENT_ID)

    client.username_pw_set(USERNAME, PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(BROKER, PORT, 60)

    # Start the processing loop
    client.loop_forever()

if __name__ == "__main__":
    main()
