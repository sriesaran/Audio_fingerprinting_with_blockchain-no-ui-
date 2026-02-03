# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import time

# Import your existing logic
# Ensure these files are in the same directory or properly installed as a package
from backend import register_audio, recognize_audio, verify_from_blockchain

app = FastAPI()

# Allow React to talk to this server
# In backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",  # 👈 THIS IS THE CRITICAL LINE FOR VITE
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> str:
    """Helper to save uploaded file temporarily"""
    file_path = os.path.join(TEMP_DIR, upload_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path

@app.post("/verify")
async def verify_audio_endpoint(file: UploadFile = File(...)):
    """
    Receives an audio file, checks for fingerprints, and verifies on blockchain.
    """
    try:
        temp_path = save_upload_file(file)
        
        # 1. Check Fingerprint Database (using your backend.py logic)
        match_id, score = recognize_audio(temp_path)
        
        # Cleanup temp file
        os.remove(temp_path)

        if match_id and score >= 30: # Using your MIN_MATCH_SCORE logic
            # 2. Verify on Blockchain
            bc_data = verify_from_blockchain(match_id)
            
            if bc_data:
                return {
                    "status": "MATCH_FOUND",
                    "match_score": score,
                    "metadata": {
                        "audio_id": bc_data["audio_id"],
                        "owner": bc_data["owner"],
                        "timestamp": bc_data["timestamp"],
                        "master_hash": bc_data["master_hash"]
                    }
                }
            else:
                return {
                    "status": "MATCH_BUT_NO_CHAIN",
                    "match_score": score,
                    "metadata": {"audio_id": match_id}
                }
        else:
            return {"status": "NO_MATCH", "match_score": score}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def register_audio_endpoint(
    file: UploadFile = File(...), 
    audio_id: str = Form(...)
):
    """
    Registers a new audio file to DB and Blockchain.
    """
    try:
        temp_path = save_upload_file(file)
        
        # Call your existing function (Modified to return status if possible, 
        # but your current void function works too)
        register_audio(temp_path, audio_id)
        
        os.remove(temp_path)
        
        return {"status": "SUCCESS", "audio_id": audio_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)