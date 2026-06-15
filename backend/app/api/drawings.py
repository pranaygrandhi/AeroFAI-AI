from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.drawing import DrawingUploadResponse
from app.services.drawing_service import DrawingService

router = APIRouter()
service = DrawingService()


@router.post("/upload", response_model=DrawingUploadResponse)
async def upload_drawing(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF drawings are supported")

    result = await service.process_pdf(file)
    return result


@router.get("/{drawing_id}")
def get_drawing(drawing_id: int):
    # Placeholder for drawing metadata lookup
    return JSONResponse({"drawing_id": drawing_id, "status": "available"})
