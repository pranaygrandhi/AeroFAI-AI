from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Characteristic(BaseModel):
    id: str
    type: str  # "dimension", "gdt", "note"
    balloon_no: int
    page: int
    x: float  # percentage, 0-100
    y: float  # percentage, 0-100
    width: float  # percentage, 0-100
    height: float  # percentage, 0-100
    requirement: str
    nominal: Optional[float] = None
    upper_tolerance: Optional[float] = None
    lower_tolerance: Optional[float] = None
    upper_limit: Optional[float] = None
    lower_limit: Optional[float] = None
    unit: str = "inch"
    measured_value: Optional[float] = None
    status: str = "pending"  # "pass", "fail", "pending"
    tool: str = "Caliper"

class PageData(BaseModel):
    page_number: int
    image: str  # base64 data-uri of the rendered page
    width: float
    height: float

class DrawingUploadResponse(BaseModel):
    drawing_id: int
    filename: str
    uploaded_at: datetime
    status: str
    confidence_score: float
    pages: List[PageData]
    characteristics: List[Characteristic]
    part_name: Optional[str] = ""
    part_number: Optional[str] = ""
    serial_number: Optional[str] = ""
    revision: Optional[str] = ""
    supplier: Optional[str] = ""
    po_number: Optional[str] = ""
    customer: Optional[str] = ""

class DrawingSummary(BaseModel):
    drawing_id: int
    filename: str
    uploaded_at: datetime
    status: str
    confidence_score: float
    part_name: Optional[str] = ""
    part_number: Optional[str] = ""
    revision: Optional[str] = ""
    characteristics_count: int
    measured_count: int
    pass_count: int
    fail_count: int

class CharacteristicsUpdatePayload(BaseModel):
    characteristics: List[Characteristic]
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    serial_number: Optional[str] = None
    revision: Optional[str] = None
    supplier: Optional[str] = None
    po_number: Optional[str] = None
    customer: Optional[str] = None
