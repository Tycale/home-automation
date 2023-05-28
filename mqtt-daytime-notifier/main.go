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
	tz := os.Getenv("TZ")

	if broker == "" || topic == "" || username == "" || password == "" {
		log.Fatal("Environment variables MQTT_BROKER, MQTT_TOPIC, MQTT_USERNAME, and MQTT_PASSWORD must be set.")
	}

	locat, error := time.LoadLocation(tz)
	if error != nil {
		panic(error)
	}

	opts := mqtt.NewClientOptions().AddBroker(broker)
	opts.SetUsername(username)
	opts.SetPassword(password)

	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		log.Fatal(token.Error())
	}

	for {
		daytime := getDaytime(locat)

		token := client.Publish(topic, 0, true, daytime)
		token.Wait()

		fmt.Printf("Published message: %s @ %s\n", daytime, time.Now().In(locat).Format("15:04:05"))
		time.Sleep(1 * time.Hour)
	}
}

func getDaytime(locat *time.Location) string {
	now := time.Now().In(locat)
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

