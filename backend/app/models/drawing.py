from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from enum import Enum

from .base import Base


class DrawingStatusEnum(str, Enum):
    draft = "draft"
    processing = "processing"
    completed = "completed"
    archived = "archived"


class CharacteristicTypeEnum(str, Enum):
    dimension = "dimension"
    gdt = "gdt"
    note = "note"


class CharacteristicStatusEnum(str, Enum):
    pending = "pending"
    pass_status = "pass"
    fail_status = "fail"


class Drawing(Base):
    __tablename__ = "drawings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    part_name = Column(String, nullable=True)
    part_number = Column(String, unique=True, nullable=True, index=True)
    serial_number = Column(String, nullable=True)
    revision = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    po_number = Column(String, nullable=True)
    customer = Column(String, nullable=True)
    
    status = Column(SQLEnum(DrawingStatusEnum), default=DrawingStatusEnum.draft)
    confidence_score = Column(Float, default=0.0)
    page_count = Column(Integer, default=1)
    
    file_path = Column(String, nullable=True)  # Path where PDF is stored
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="drawings")
    characteristics = relationship("Characteristic", back_populates="drawing", cascade="all, delete-orphan")
    balloons = relationship("Balloon", back_populates="drawing", cascade="all, delete-orphan")
    pages = relationship("DrawingPage", back_populates="drawing", cascade="all, delete-orphan")
    revisions = relationship("DrawingRevision", back_populates="drawing", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="drawing")


class Characteristic(Base):
    __tablename__ = "characteristics"

    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    
    type = Column(SQLEnum(CharacteristicTypeEnum), nullable=False)
    balloon_no = Column(Integer, nullable=False)
    page_number = Column(Integer, default=1)
    
    # Position on drawing (percentage based, 0-100)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    
    # Dimension specifications
    requirement = Column(String, nullable=False)
    nominal = Column(Float, nullable=True)
    upper_tolerance = Column(Float, nullable=True)
    lower_tolerance = Column(Float, nullable=True)
    upper_limit = Column(Float, nullable=True)
    lower_limit = Column(Float, nullable=True)
    unit = Column(String, default="inch")
    
    # GD&T and notes
    gdt_symbol = Column(String, nullable=True)  # e.g., "perpendicularity", "parallelism"
    datum_reference = Column(String, nullable=True)  # e.g., "A", "B", "C"
    notes = Column(Text, nullable=True)
    
    # Inspection results
    measured_value = Column(Float, nullable=True)
    status = Column(SQLEnum(CharacteristicStatusEnum), default=CharacteristicStatusEnum.pending)
    tool = Column(String, nullable=True)  # e.g., "Caliper", "Micrometer"
    inspector_comments = Column(Text, nullable=True)
    
    # Metadata
    confidence_score = Column(Float, default=0.0)
    source = Column(String, default="auto")  # "auto" or "manual"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drawing = relationship("Drawing", back_populates="characteristics")


class Balloon(Base):
    __tablename__ = "balloons"

    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    characteristic_id = Column(Integer, ForeignKey("characteristics.id"), nullable=True)
    
    balloon_number = Column(Integer, nullable=False)
    page_number = Column(Integer, default=1)
    
    # Balloon position
    cx = Column(Float, nullable=False)  # Center X (percentage)
    cy = Column(Float, nullable=False)  # Center Y (percentage)
    radius = Column(Float, default=2.0)
    
    # Leader line end point
    leader_x = Column(Float, nullable=True)
    leader_y = Column(Float, nullable=True)
    
    # Balloon state
    is_placed = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drawing = relationship("Drawing", back_populates="balloons")


class DrawingPage(Base):
    __tablename__ = "drawing_pages"

    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    
    page_number = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    
    # Cached image as base64
    image_data = Column(Text, nullable=True)
    
    # OCR results
    ocr_text = Column(Text, nullable=True)
    vector_text = Column(Text, nullable=True)
    merged_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drawing = relationship("Drawing", back_populates="pages")


class DrawingRevision(Base):
    __tablename__ = "drawing_revisions"

    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=False)
    
    revision_number = Column(String, nullable=False)
    revision_date = Column(DateTime, nullable=True)
    
    # Changes metadata
    change_description = Column(Text, nullable=True)
    characteristics_changed = Column(Integer, default=0)
    
    # Stored comparison
    comparison_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    drawing = relationship("Drawing", back_populates="revisions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drawing_id = Column(Integer, ForeignKey("drawings.id"), nullable=True)
    
    action = Column(String, nullable=False)  # "create", "update", "delete", "export"
    entity_type = Column(String, nullable=False)  # "drawing", "characteristic", "balloon"
    entity_id = Column(Integer, nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    drawing = relationship("Drawing", back_populates="audit_logs")
