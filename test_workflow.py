#!/usr/bin/env python
"""Smoke test: upload PDF → poll status → export AS9102."""

import requests
import time
import json

API_BASE = "http://localhost:8000"

def test_workflow():
    """Test full upload → status → export workflow."""
    print("[TEST] Starting workflow test...")
    
    # Create a minimal PDF-like file for testing
    # (real PDF parsing will fail but endpoint should work)
    pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"
    
    # Step 1: Upload
    print("\n[1] Uploading PDF...")
    try:
        files = {"file": ("test_drawing.pdf", pdf_content, "application/pdf")}
        resp = requests.post(f"{API_BASE}/api/drawings/upload", files=files, timeout=5)
        print(f"    Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"    Error: {resp.text}")
            return
        upload_result = resp.json()
        drawing_id = upload_result.get("drawing_id")
        print(f"    Drawing ID: {drawing_id}")
        print(f"    Response: {json.dumps(upload_result, indent=2, default=str)}")
    except Exception as e:
        print(f"    ERROR: {e}")
        return
    
    # Step 2: Poll status
    print(f"\n[2] Polling status for drawing {drawing_id}...")
    for attempt in range(10):
        try:
            resp = requests.get(f"{API_BASE}/api/drawings/{drawing_id}/status", timeout=5)
            print(f"    Attempt {attempt + 1}: {resp.status_code}")
            if resp.status_code == 200:
                status_data = resp.json()
                print(f"    Status: {status_data.get('status')}")
                if status_data.get("status") in ("processed", "error"):
                    print(f"    Done! Result: {json.dumps(status_data, indent=2, default=str)}")
                    break
            time.sleep(0.5)
        except Exception as e:
            print(f"    Attempt {attempt + 1} ERROR: {e}")
    
    # Step 3: Export
    print(f"\n[3] Exporting AS9102 for drawing {drawing_id}...")
    try:
        resp = requests.get(f"{API_BASE}/api/drawings/{drawing_id}/export", timeout=5)
        print(f"    Status: {resp.status_code}")
        if resp.status_code == 200:
            csv_content = resp.text
            print(f"    CSV content (first 300 chars):\n{csv_content[:300]}")
        else:
            print(f"    Error: {resp.text}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    print("\n[TEST] Workflow test complete!")

if __name__ == "__main__":
    test_workflow()
