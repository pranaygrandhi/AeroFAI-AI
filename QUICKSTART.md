# AeroFAI-AI Enhancement - Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- pip package manager

---

## 🚀 Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in the `backend` directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/aerofai

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# API Settings
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### 3. Initialize Database
The database will automatically initialize on first app startup. You can also manually init:
```bash
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
"
```

### 4. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

**Verify it's working:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok", "environment": "development"}
```

---

## 🎨 Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 🧪 Testing the New Features

### 1. Test OCR Engine
```python
from app.ai.ocr_engine import OcrEngine

engine = OcrEngine()
# Will process PaddleOCR on any pages provided
```

### 2. Test AS9102 Form Generation
```bash
# Export Form 3 for drawing ID 1
curl http://localhost:8000/api/drawings/1/export/form-3 \
  --output form3.xlsx
```

### 3. Test Database Operations
```bash
# Get drawing pages
curl http://localhost:8000/api/drawings/1/pages

# Get characteristics
curl http://localhost:8000/api/drawings/1/characteristics

# Update characteristics
curl -X POST http://localhost:8000/api/drawings/1/characteristics \
  -H "Content-Type: application/json" \
  -d '{"characteristics": [...]}'
```

### 4. Test UI Components
- Navigate to `http://localhost:3000/editor?id=1` for the enhanced editor
- Try creating balloons manually with the new **Manual Balloon Tool**
- Edit characteristics inline in the **Editable Characteristic Table**
- Navigate multiple pages with the **Multi-Page Viewer**

---

## 📊 Using the New Features

### Manual Balloon Creation
1. Open editor: `/editor?id={drawing_id}`
2. Click "Create Balloon" button
3. Click on the drawing to place balloons
4. Drag to reposition, click number to renumber
5. Select "Edit Selected" to modify properties

### Inline Characteristic Editing
1. In the results view, find the characteristic table
2. Click any cell to edit (numerical validation included)
3. Use dropdown for status changes
4. Filter by status (Pass/Fail/Pending)
5. View real-time statistics

### Multi-Page Navigation
1. Upload a multi-page PDF
2. Use Previous/Next buttons or page input
3. Scroll wheel to zoom in/out
4. Middle-click to pan
5. Click "Reset" to return to fit view

### Export AS9102 Forms
```bash
# Export all three forms for drawing ID 123

# Form 1 (FAIR - First Article Inspection Report)
GET /api/drawings/123/export/form-1

# Form 2 (Inspection Planning)
GET /api/drawings/123/export/form-2

# Form 3 (Characteristics Accountability - Results)
GET /api/drawings/123/export/form-3
```

---

## 🐛 Troubleshooting

### Database Connection Failed
```
Error: Could not connect to database
```
**Solution:**
1. Verify PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify credentials
4. Ensure database exists: `createdb aerofai`

### PaddleOCR Not Working
```
Error: PaddleOCR not installed or GPU issues
```
**Solution:**
1. `pip install paddleocr==2.7.0`
2. For CPU-only: `pip install paddleocr[cpu]`
3. For GPU (CUDA): Ensure GPU drivers installed

### Frontend Not Connecting to Backend
```
Error: Failed to fetch from API
```
**Solution:**
1. Backend must be running on `http://localhost:8000`
2. Check NEXT_PUBLIC_API_URL in `.env.local`
3. Verify CORS is enabled (already configured)
4. Check browser console for errors

### Import Errors in Backend
```
ModuleNotFoundError: No module named 'app'
```
**Solution:**
```bash
# Make sure you're in the backend directory
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --reload
```

---

## 📈 Performance Optimization

### Backend Optimization
```python
# Connection pooling is auto-configured
# For high-concurrency, increase pool size in database.py:
pool_size=20        # Default connections
max_overflow=10     # Additional temporary connections
```

### Frontend Optimization
```bash
# Build for production
npm run build

# Start production server
npm start
```

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_drawing_user ON drawings(user_id);
CREATE INDEX idx_char_drawing ON characteristics(drawing_id);
CREATE INDEX idx_balloon_drawing ON balloons(drawing_id);
CREATE INDEX idx_pages_drawing ON drawing_pages(drawing_id);
```

---

## 📚 API Documentation

### Get Drawing Pages
```
GET /api/drawings/{drawing_id}/pages

Response:
[
  {
    "page_number": 1,
    "width": 2560,
    "height": 1920,
    "image_data": "data:image/png;base64,...",
    "ocr_text": "Extracted text...",
    "ocr_confidence": 0.95
  }
]
```

### Get Characteristics
```
GET /api/drawings/{drawing_id}/characteristics?page=1

Response:
[
  {
    "id": 1,
    "balloon_no": 1,
    "type": "dimension",
    "requirement": "Ø12.5 ±0.1",
    "nominal": 12.5,
    "upper_limit": 12.6,
    "lower_limit": 12.4,
    "measured_value": 12.48,
    "status": "pass"
  }
]
```

### Update Characteristics
```
POST /api/drawings/{drawing_id}/characteristics

Request:
{
  "characteristics": [
    {
      "id": 1,
      "balloon_no": 1,
      "measured_value": 12.47,
      "status": "pass"
    }
  ],
  "part_name": "Updated Part Name"
}

Response:
{
  "success": true,
  "updated_count": 1
}
```

### Export Forms
```
GET /api/drawings/{drawing_id}/export/form-1  # Returns .xlsx
GET /api/drawings/{drawing_id}/export/form-2  # Returns .xlsx
GET /api/drawings/{drawing_id}/export/form-3  # Returns .xlsx
```

---

## 📦 Database Schema Overview

### Users Table
```
- id (PK)
- email (unique)
- full_name
- hashed_password
- role (admin, quality_manager, inspector, engineer, viewer)
- is_active
- created_at, updated_at
```

### Drawings Table
```
- id (PK)
- user_id (FK)
- filename
- part_name, part_number, revision
- status (draft, processing, completed, archived)
- confidence_score
- page_count
- created_at, updated_at, uploaded_at
```

### Characteristics Table
```
- id (PK)
- drawing_id (FK)
- balloon_no
- type (dimension, gdt, note)
- requirement
- nominal, upper_tolerance, lower_tolerance
- upper_limit, lower_limit
- measured_value
- status (pending, pass, fail)
- confidence_score
- created_at, updated_at
```

### DrawingPages Table
```
- id (PK)
- drawing_id (FK)
- page_number
- width, height
- image_data (base64)
- ocr_text, vector_text, merged_text
- ocr_confidence
```

### AuditLog Table
```
- id (PK)
- user_id (FK)
- drawing_id (FK)
- action (create, update, delete, export)
- entity_type
- old_values, new_values (JSON)
- created_at
```

---

## ✅ Verification Checklist

After setup, verify everything is working:

- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend loads: `http://localhost:3000`
- [ ] Can upload PDF
- [ ] Can create balloons manually
- [ ] Can edit characteristics inline
- [ ] Can view multi-page drawings
- [ ] Can export AS9102 forms
- [ ] Database queries work
- [ ] OCR processes pages
- [ ] No console errors

---

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs (if running with --reload)
# Check terminal where uvicorn is running

# Frontend logs
# Check browser console (F12)
```

### Debug Mode
```python
# In backend .env
ENVIRONMENT=development  # Shows full error messages and SQL logging
```

### Enable SQL Logging
```python
# In database.py, set echo=True
engine = create_async_engine(
    str(settings.database_url),
    echo=True,  # This prints all SQL queries
)
```

---

## 📞 Support Resources

1. **Code Documentation**: See docstrings in all files
2. **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md`
3. **README**: See project `README.md` for architecture overview
4. **Inline Comments**: Complex logic has explanatory comments

---

**Ready to go!** 🎉 Start the backend and frontend, then navigate to `http://localhost:3000`
