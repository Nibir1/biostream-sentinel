-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: device_telemetry (Hot Data / Recent)
-- Stores the validated telemetry data temporarily or permanently depending on retention policy
CREATE TABLE IF NOT EXISTS device_telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(50) NOT NULL,
    patient_id_hash VARCHAR(64) NOT NULL, -- PII Hashed
    timestamp TIMESTAMPTZ NOT NULL,
    heart_rate INTEGER NOT NULL,
    spo2 FLOAT NOT NULL,
    battery_level FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Index for time-series queries
CREATE INDEX idx_telemetry_device_time ON device_telemetry(device_id, timestamp DESC);

-- Table: anomalies (AI Results)
-- Stores only high-risk events detected by the Isolation Forest
CREATE TABLE IF NOT EXISTS anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telemetry_id UUID REFERENCES device_telemetry(id),
    device_id VARCHAR(50) NOT NULL,
    anomaly_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    detected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anomalies_risk ON anomalies(risk_level);