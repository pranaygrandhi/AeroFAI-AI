from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from io import StringIO, BytesIO
import csv

from ..services.drawing_service import DrawingService

router = APIRouter()
service = DrawingService()


@router.get("/{drawing_id}/status")
def get_status(drawing_id: int):
    result = service._read_result(drawing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not Found")
    return JSONResponse(result)


@router.get("/{drawing_id}/result")
def get_result(drawing_id: int):
    result = service._read_result(drawing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not Found")
    return JSONResponse(result)


@router.get("/{drawing_id}/export")
def export_as9102(drawing_id: int):
    """Generate a simple AS9102-style CSV export from the stored result.

    This is a simplified demo export: if `characteristics` exist they will be
    written to CSV rows; otherwise basic metadata is returned.
    """
    result = service._read_result(drawing_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not Found")

    # Build CSV in-memory
    buf = StringIO()
    writer = csv.writer(buf)

    # header metadata
    writer.writerow(["AS9102 Export"])
    writer.writerow(["drawing_id", result.get("drawing_id")])
    writer.writerow(["filename", result.get("filename")])
    writer.writerow(["uploaded_at", result.get("uploaded_at")])
    writer.writerow(["status", result.get("status")])
    writer.writerow(["confidence_score", result.get("confidence_score")])
    writer.writerow([])

    # characteristics table
    writer.writerow(["characteristic_id", "balloon", "description", "value"])
    chars = result.get("characteristics") or []
    if chars:
        for c in chars:
            # expect c to contain these keys in pipeline; fall back to blank
            writer.writerow([c.get("id") or "", c.get("balloon") or "", c.get("description") or "", c.get("value") or ""])
    else:
        # fallback: write a placeholder row
        writer.writerow(["N/A", "N/A", "No characteristics extracted", "N/A"])

    csv_bytes = buf.getvalue().encode("utf-8")
    buf.close()

    filename = f"AS9102_export_{drawing_id}.csv"
    return StreamingResponse(BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
