import logging
import json
import time
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class JsonFormatter(logging.Formatter):
    """Formats log records as a JSON object."""
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "correlation_id": getattr(record, "correlation_id", None),
        }
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    """Configures the root logger to output JSON."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attaches a unique ID to every request for traceability."""
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        # Store in request state for access in endpoints
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log the request completion
        logger = logging.getLogger("api.access")
        extra = {"correlation_id": correlation_id}
        # We manually attach the attribute to the record in a real implementation, 
        # or use a ContextVar. For simplicity here:
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s", extra=extra)
        
        response.headers["X-Correlation-ID"] = correlation_id
        return response