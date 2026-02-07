from app.services.storage import storage

async def get_device_context(device_id: str) -> str:
    """
    Fetches the last 10 telemetry records and any anomalies for a specific device.
    """
    if not storage.pool:
        return "System Error: Database not connected."

    async with storage.pool.acquire() as conn:
        # 1. Fetch recent telemetry (Vitals)
        rows = await conn.fetch('''
            SELECT timestamp, heart_rate, spo2, battery_level 
            FROM device_telemetry 
            WHERE device_id = $1 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', device_id)
        
        # 2. Fetch recent anomalies (Risk)
        alerts = await conn.fetch('''
            SELECT risk_level, anomaly_score, detected_at 
            FROM anomalies 
            WHERE device_id = $1 
            ORDER BY detected_at DESC 
            LIMIT 5
        ''', device_id)

    if not rows:
        return f"No recent data found for {device_id}."

    # Format as a clean string for the LLM
    context = f"--- TELEMETRY LOG FOR {device_id} ---\n"
    for r in rows:
        context += f"Time: {r['timestamp']}, HR: {r['heart_rate']} bpm, SPO2: {r['spo2']}%\n"
    
    context += "\n--- RECENT ALERTS ---\n"
    for a in alerts:
        context += f"Time: {a['detected_at']}, Risk: {a['risk_level']}, Score: {a['anomaly_score']:.4f}\n"
        
    return context