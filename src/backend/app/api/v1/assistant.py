from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.context import get_device_context
from app.services.report import generate_medical_pdf
import re
import logging

# Initialize Router
router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OpenAI Client
# We check if the key exists to prevent startup errors, though Settings usually enforces it.
client = None
if settings.OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest):
    """
    Context-Aware Chatbot endpoint.
    1. Parses user message for Device IDs (e.g., WEARABLE-007).
    2. Fetches real-time telemetry context from Postgres.
    3. Sends prompt + context to OpenAI GPT-4o-mini.
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI API Key not configured.")

    user_query = req.message
    
    # System Prompt Engineering
    system_context = """
    You are BioStream Sentinel, an advanced AI assistant for cardiac monitoring.
    Your goal is to assist clinicians in analyzing patient telemetry.
    
    Guidelines:
    - Analyze the provided Patient Data carefully.
    - If Heart Rate is > 100 or < 50, flag as abnormal.
    - If SPO2 is < 95%, flag as hypoxia risk.
    - Be professional, concise, and purely medical in tone.
    - If no data is provided, answer general medical questions but state you lack specific patient context.
    """

    # 1. Detect Device ID (Regex matches WEARABLE-001 to WEARABLE-999)
    # Simulator uses WEARABLE-XXX format.
    device_match = re.search(r"(WEARABLE-\d{3})", user_query, re.IGNORECASE)
    
    if device_match:
        device_id = device_match.group(1).upper()
        logger.info(f"AI: Detected intent for device {device_id}")
        
        # RAG: Fetch DB Data
        try:
            db_context = await get_device_context(device_id)
            system_context += f"\n\n--- CURRENT PATIENT DATA ({device_id}) ---\n{db_context}\n-----------------------------------"
        except Exception as e:
            logger.error(f"AI: Failed to fetch context: {e}")
            system_context += f"\n\n(System Error: Could not retrieve live data for {device_id})"
    else:
        system_context += "\n\n(No specific device ID detected in query. Answer based on general medical knowledge.)"

    # 2. Call OpenAI API
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_query}
            ],
            temperature=0.3, # Low temperature for more deterministic/factual answers
            max_tokens=500
        )
        return {"reply": response.choices[0].message.content}
        
    except Exception as e:
        logger.error(f"AI: OpenAI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")

@router.post("/generate-report")
async def create_report(req: ChatRequest):
    """
    Generates a PDF report based on the AI's explanation or raw text.
    Returns a downloadable PDF stream.
    """
    try:
        # Generate PDF in-memory using ReportLab
        pdf_buffer = generate_medical_pdf("AI-GENERATED CLINICAL REPORT", req.message)
        
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=clinical_report.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")