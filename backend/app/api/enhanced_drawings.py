"""
Enhanced API endpoints for AS9102 drawing management, characteristics, and form generation.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..repositories import (
    DrawingRepository,
    CharacteristicRepository,
    BalloonRepository,
    DrawingPageRepository,
)
from ..schemas.drawing import (
    Characteristic,
    CharacteristicsUpdatePayload,
    DrawingUploadResponse,
)
from ..ai.as9102_generator import AS9102Generator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{drawing_id}")
async def get_drawing(drawing_id: int, db: AsyncSession = Depends(get_db)):
    """Get drawing with all related data."""
    drawing_repo = DrawingRepository(db)
    drawing = await drawing_repo.get_drawing_with_characteristics(drawing_id)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    return {
        "id": drawing.id,
        "filename": drawing.filename,
        "part_name": drawing.part_name,
        "part_number": drawing.part_number,
        "revision": drawing.revision,
        "status": drawing.status.value,
        "created_at": drawing.created_at,
        "page_count": drawing.page_count,
    }


@router.get("/{drawing_id}/pages")
async def get_drawing_pages(
    drawing_id: int, db: AsyncSession = Depends(get_db)
):
    """Get all pages for a drawing."""
    page_repo = DrawingPageRepository(db)
    
    # Verify drawing exists
    drawing_repo = DrawingRepository(db)
    drawing = await drawing_repo.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    pages = await page_repo.get_by_drawing(drawing_id)

    return [
        {
            "page_number": p.page_number,
            "width": p.width,
            "height": p.height,
            "image_data": p.image_data,
            "ocr_text": p.ocr_text,
            "vector_text": p.vector_text,
        }
        for p in pages
    ]


@router.get("/{drawing_id}/pages/{page_number}")
async def get_drawing_page(
    drawing_id: int, page_number: int, db: AsyncSession = Depends(get_db)
):
    """Get a specific page for a drawing."""
    page_repo = DrawingPageRepository(db)
    page = await page_repo.get_page(drawing_id, page_number)

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    return {
        "page_number": page.page_number,
        "width": page.width,
        "height": page.height,
        "image_data": page.image_data,
        "ocr_text": page.ocr_text,
        "vector_text": page.vector_text,
        "merged_text": page.merged_text,
        "ocr_confidence": page.ocr_confidence,
    }


@router.get("/{drawing_id}/characteristics")
async def get_characteristics(
    drawing_id: int, page: Optional[int] = None, db: AsyncSession = Depends(get_db)
):
    """Get characteristics for a drawing, optionally filtered by page."""
    char_repo = CharacteristicRepository(db)
    characteristics = await char_repo.get_by_drawing(drawing_id)

    if page:
        characteristics = [c for c in characteristics if c.page_number == page]

    return [
        {
            "id": c.id,
            "balloon_no": c.balloon_no,
            "type": c.type.value,
            "requirement": c.requirement,
            "nominal": c.nominal,
            "upper_tolerance": c.upper_tolerance,
            "lower_tolerance": c.lower_tolerance,
            "upper_limit": c.upper_limit,
            "lower_limit": c.lower_limit,
            "unit": c.unit,
            "measured_value": c.measured_value,
            "status": c.status.value,
            "page_number": c.page_number,
            "x": c.x,
            "y": c.y,
        }
        for c in characteristics
    ]


@router.post("/{drawing_id}/characteristics")
async def update_characteristics(
    drawing_id: int,
    payload: CharacteristicsUpdatePayload,
    db: AsyncSession = Depends(get_db),
):
    """Update characteristics for a drawing."""
    char_repo = CharacteristicRepository(db)
    drawing_repo = DrawingRepository(db)

    # Verify drawing exists
    drawing = await drawing_repo.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    # Prepare characteristic data
    char_data_list = []
    for char in payload.characteristics:
        char_dict = char.model_dump()
        char_dict["drawing_id"] = drawing_id
        char_data_list.append(char_dict)

    # Bulk update
    updated = await char_repo.bulk_update_characteristics(drawing_id, char_data_list)

    # Update drawing metadata if provided
    updates = {}
    if payload.part_name:
        updates["part_name"] = payload.part_name
    if payload.part_number:
        updates["part_number"] = payload.part_number
    if payload.revision:
        updates["revision"] = payload.revision

    if updates:
        await drawing_repo.update(drawing_id, updates)

    await db.commit()

    return {
        "success": True,
        "updated_count": len(updated),
        "characteristics": [
            {
                "id": c.id,
                "balloon_no": c.balloon_no,
                "status": c.status.value,
            }
            for c in updated
        ],
    }


@router.get("/{drawing_id}/export/form-1")
async def export_form_1(
    drawing_id: int, db: AsyncSession = Depends(get_db)
):
    """Export AS9102 Form 1 (FAIR)."""
    drawing_repo = DrawingRepository(db)
    drawing = await drawing_repo.get(drawing_id)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    generator = AS9102Generator()
    excel_file = generator.generate_form_1(
        drawing_id=drawing_id,
        part_name=drawing.part_name or "",
        part_number=drawing.part_number or "",
        revision=drawing.revision or "",
        supplier=drawing.supplier or "",
        customer=drawing.customer or "",
    )

    return StreamingResponse(
        iter([excel_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=AS9102_Form1_{drawing_id}.xlsx"},
    )


@router.get("/{drawing_id}/export/form-2")
async def export_form_2(
    drawing_id: int, db: AsyncSession = Depends(get_db)
):
    """Export AS9102 Form 2 (Inspection Planning)."""
    drawing_repo = DrawingRepository(db)
    char_repo = CharacteristicRepository(db)
    
    drawing = await drawing_repo.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    characteristics = await char_repo.get_by_drawing(drawing_id)

    generator = AS9102Generator()
    excel_file = generator.generate_form_2(
        drawing_id=drawing_id,
        part_name=drawing.part_name or "",
        part_number=drawing.part_number or "",
        revision=drawing.revision or "",
        supplier=drawing.supplier or "",
        customer=drawing.customer or "",
        characteristics=[
            {
                "balloon_no": c.balloon_no,
                "requirement": c.requirement,
                "type": c.type.value,
                "nominal": c.nominal,
                "upper_limit": c.upper_limit,
                "lower_limit": c.lower_limit,
                "tool": c.tool,
            }
            for c in characteristics
        ],
    )

    return StreamingResponse(
        iter([excel_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=AS9102_Form2_{drawing_id}.xlsx"},
    )


@router.get("/{drawing_id}/export/form-3")
async def export_form_3(
    drawing_id: int, db: AsyncSession = Depends(get_db)
):
    """Export AS9102 Form 3 (Inspection Results)."""
    drawing_repo = DrawingRepository(db)
    char_repo = CharacteristicRepository(db)
    
    drawing = await drawing_repo.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    characteristics = await char_repo.get_by_drawing(drawing_id)

    generator = AS9102Generator()
    excel_file = generator.generate_form_3(
        drawing_id=drawing_id,
        part_name=drawing.part_name or "",
        part_number=drawing.part_number or "",
        revision=drawing.revision or "",
        serial_number=drawing.serial_number or "",
        supplier=drawing.supplier or "",
        customer=drawing.customer or "",
        characteristics=[
            {
                "balloon_no": c.balloon_no,
                "requirement": c.requirement,
                "type": c.type.value,
                "nominal": c.nominal,
                "upper_limit": c.upper_limit,
                "lower_limit": c.lower_limit,
                "unit": c.unit,
                "measured_value": c.measured_value,
                "status": c.status.value,
            }
            for c in characteristics
        ],
    )

    return StreamingResponse(
        iter([excel_file.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=AS9102_Form3_{drawing_id}.xlsx"},
    )
