package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

const (
	API_URL       = "http://localhost:8000/api/v1/telemetry"
	DEVICE_COUNT  = 10
	SEND_INTERVAL = 1 * time.Second
)

// Global HTTP client with timeout to prevent hanging connections
var httpClient = &http.Client{
	Timeout: 5 * time.Second,
}

func main() {
	fmt.Printf("🚀 Starting BioStream Simulator with %d devices...\n", DEVICE_COUNT)
	fmt.Printf("📡 Target: %s\n", API_URL)

	var wg sync.WaitGroup

	// Launch a goroutine for each device
	for i := 1; i <= DEVICE_COUNT; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			worker(id)
		}(i)
	}

	// Keep main thread alive
	wg.Wait()
}

func worker(id int) {
	sim := NewDeviceSimulator(id)
	logger := log.New(log.Writer(), fmt.Sprintf("[DEV-%03d] ", id), log.LstdFlags)

	for {
		payload := sim.GenerateNextPayload()

		err := sendTelemetry(payload)
		if err != nil {
			logger.Printf("❌ Failed to send: %v", err)
		} else {
			logger.Printf("✅ Sent: HR=%d BPM, SPO2=%.1f%%", payload.HeartRate, payload.SPO2)
		}

		time.Sleep(SEND_INTERVAL)
	}
}

func sendTelemetry(data TelemetryPayload) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	// Retry logic (Simple linear backoff)
	maxRetries := 3
	for i := 0; i < maxRetries; i++ {
		resp, err := httpClient.Post(API_URL, "application/json", bytes.NewBuffer(jsonData))

		if err == nil {
			defer resp.Body.Close()
			if resp.StatusCode == 202 {
				return nil // Success
			}
			// If validation fails (422), don't retry, it's our fault
			if resp.StatusCode == 422 {
				return fmt.Errorf("server rejected data (422 validation error)")
			}
			return fmt.Errorf("server returned status: %d", resp.StatusCode)
		}

		// Wait before retrying
		time.Sleep(500 * time.Millisecond)
	}

	return fmt.Errorf("max retries exceeded")
}
