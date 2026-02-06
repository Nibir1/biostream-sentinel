package main

import (
	"fmt"
	"math"
	"math/rand"
	"time"
)

// TelemetryPayload matches the Python Pydantic Schema exactly
type TelemetryPayload struct {
	DeviceID     string  `json:"device_id"`
	PatientID    string  `json:"patient_id"`
	Timestamp    string  `json:"timestamp"`
	HeartRate    int     `json:"heart_rate"`
	SPO2         float64 `json:"spo2"`
	BatteryLevel float64 `json:"battery_level"`
}

// Simulator state for a single device
type DeviceSimulator struct {
	DeviceID  string
	PatientID string
	Tick      float64 // Internal counter for sine wave
}

func NewDeviceSimulator(id int) *DeviceSimulator {
	return &DeviceSimulator{
		DeviceID:  fmt.Sprintf("WEARABLE-%03d", id),
		PatientID: fmt.Sprintf("PATIENT-%03d", id),
		Tick:      rand.Float64() * 100, // Random start phase
	}
}

// GenerateNextPayload creates a realistic data point
func (s *DeviceSimulator) GenerateNextPayload() TelemetryPayload {
	s.Tick += 0.1 // Advance time

	// Simulate Heart Rate: Base 75 + Sine Wave Variation + Random Noise
	// This creates a smooth curve between 60 and 90 BPM mostly
	baseHR := 75.0
	variation := 15.0 * math.Sin(s.Tick)
	noise := (rand.Float64() - 0.5) * 5.0
	hr := int(baseHR + variation + noise)

	// Randomly introduce a spike (anomaly) every ~100 ticks
	if rand.Intn(100) == 0 {
		hr += 50 // Sudden spike to ~130-140
	}

	// Simulate SPO2: Mostly stable 97-100, rarely drops
	spo2 := 97.0 + (rand.Float64() * 3.0)
	if rand.Intn(50) == 0 {
		spo2 -= 5.0 // Drop to 92ish
	}

	return TelemetryPayload{
		DeviceID:     s.DeviceID,
		PatientID:    s.PatientID,
		Timestamp:    time.Now().Format(time.RFC3339),
		HeartRate:    hr,
		SPO2:         math.Round(spo2*10) / 10, // Round to 1 decimal
		BatteryLevel: 85.5,                     // Static for now
	}
}
