from datetime import datetime
from pydantic import BaseModel


class DrawingUploadResponse(BaseModel):
    drawing_id: int
    filename: str
    uploaded_at: datetime
    status: str
    confidence_score: float
