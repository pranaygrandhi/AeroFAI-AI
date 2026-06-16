from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from ..schemas.drawing import DrawingUploadResponse
from ..services.drawing_service import DrawingService

router = APIRouter()
service = DrawingService()


class BuildDatasetRequest(BaseModel):
    results_dir: Optional[str] = "./tmp"
    output_dir: Optional[str] = None
    train_ratio: float = 0.8


class TrainModelRequest(BaseModel):
    epochs: int = 20
    model: str = "yolov8n.pt"
    run_name: str = "train"


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


@router.post("/training/build_dataset")
def build_training_dataset(payload: BuildDatasetRequest):
    result = service.build_training_dataset(
        results_dir=payload.results_dir,
        output_dir=payload.output_dir,
        train_ratio=payload.train_ratio,
    )
    return result


@router.post("/training/train")
def train_model(payload: TrainModelRequest):
    result = service.train_model(
        epochs=payload.epochs,
        model=payload.model,
        run_name=payload.run_name,
    )
    return result


@router.get("/training/weights")
def list_training_weights():
    return {"weights": service.list_model_weights()}


class UpdateCharacteristicsRequest(BaseModel):
    characteristics: list


@router.post("/{drawing_id}/characteristics")
def update_characteristics(drawing_id: int, payload: UpdateCharacteristicsRequest):
    try:
        updated = service.update_characteristics(drawing_id, payload.characteristics)
        return JSONResponse(updated)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drawing result not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
