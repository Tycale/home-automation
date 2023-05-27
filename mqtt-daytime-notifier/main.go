package main

import (
	"fmt"
	"log"
	"os"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

func main() {
	broker := os.Getenv("MQTT_BROKER")
	topic := os.Getenv("MQTT_TOPIC")
	username := os.Getenv("MQTT_USERNAME")
	password := os.Getenv("MQTT_PASSWORD")

	opts := mqtt.NewClientOptions().AddBroker(broker)
	opts.SetUsername(username)
	opts.SetPassword(password)

	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		log.Fatal(token.Error())
	}

	for {
		daytime := getDaytime()

		token := client.Publish(topic, 0, false, daytime)
		token.Wait()

		fmt.Printf("Published message: %s\n", daytime)
		time.Sleep(1 * time.Hour)
	}
}

func getDaytime() string {
	now := time.Now()
	hour := now.Hour()

	switch {
	case hour >= 22 || hour < 6:
		return "night"
	case hour >= 6 && hour < 9:
		return "sunrise"
	case hour >= 9 && hour < 12:
		return "morning"
	case hour >= 12 && hour < 18:
		return "afternoon"
	default:
		return "evening"
	}
}

