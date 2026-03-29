from fastapi import FastAPI, UploadFile, File
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import psycopg2
import io
from datetime import datetime
import time

from noice import clean_audio

app = FastAPI()

def get_connection():
    while True:
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port="5432"
            )
            print("✅ Veritabanına bağlandı!")
            return conn
        except psycopg2.OperationalError:
            print("⏳ Veritabanı hazır değil, 2 saniye bekleniyor...")
            time.sleep(2)

conn = get_connection()
cur = conn.cursor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ana sayfa
@app.get("/")
async def root():
    return FileResponse("static/arayüz.html", media_type="text/html")

#------------------------------------------------------------
# Kayıt yükleme endpointi
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):

        
    content = await file.read()
    filename = file.filename

    filepath = f"uploads/{file.filename}"
    
    with open(filepath, "wb") as f:
        f.write(content)
   
   
    # DB'ye kaydet 
    cur.execute(
        "INSERT INTO audio_files (filename, data) VALUES (%s, %s) RETURNING id",
        (filename, psycopg2.Binary(content))
    )
    file_id = cur.fetchone()[0]

    # metadata kaydet
    cur.execute(
        "INSERT INTO audio_metadata (file_id, device_id, duration, created_at) VALUES (%s, %s, %s, %s)",
        (file_id, "device_1", 0.0, datetime.now())
    )
    conn.commit()

    clean_filename = f"clean_{file.filename}"  # zaten .wav geliyor
    clean_path = f"uploads/{clean_filename}"
    
    try:
        clean_audio(filepath, clean_path)

        # Temizlenmiş veriyi de DB'ye kaydet
        with open(clean_path, "rb") as f:
            clean_content = f.read()

        cur.execute(
            "INSERT INTO audio_files (filename, data) VALUES (%s, %s) RETURNING id",
            (clean_filename, psycopg2.Binary(clean_content))
        )
        clean_file_id = cur.fetchone()[0]

        # Temizlenmiş dosya için metadata
        cur.execute(
            "INSERT INTO audio_metadata (file_id, device_id, duration, created_at) VALUES (%s, %s, %s, %s)",
            (clean_file_id, "device_1", 0.0, datetime.now())
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
        
    return {"message": "uploaded and cleaned"}


#------------------------------------------------------------
# Kayıtları listeleme endpointi (Ham ve temiz dosyaları birlikte döndürür)
@app.get("/recordings")
async def list_recordings():
    files = os.listdir(UPLOAD_FOLDER)
    raw_files = [f for f in files if not f.startswith("clean_") and f.endswith(".wav")]

    recordings = []
    for file in raw_files:
        clean_filename = f"clean_{file}"
        recordings.append({
            "filename": file,
            "raw_url": f"/audios/{file}",
            "clean_url": f"/audios/{clean_filename}"
        })

    return JSONResponse(content=recordings)

#------------------------------------------------------------
# Kayıtları getirme endpointi 
@app.get("/audios/{filename}") 
async def get_audio(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(file_path):
        # Dosya türüne göre media type belirle
        media_type = "audio/wav" if filename.endswith(".wav") else "audio/webm"
        return FileResponse(file_path, media_type=media_type)
    else:
        return JSONResponse(content={"error": "Dosya bulunamadı"}, status_code=404)

#------------------------------------------------------------
# Kayıtları silme endpointi 
@app.delete("/delete/{filename}") 
async def delete_audio(filename: str):
    raw_path = os.path.join(UPLOAD_FOLDER, filename)
    clean_path = os.path.join(UPLOAD_FOLDER, f"clean_{filename.replace('.webm', '.wav')}")
    
    deleted = False
    if os.path.exists(raw_path):
        os.remove(raw_path)
        deleted = True
    if os.path.exists(clean_path):
        os.remove(clean_path)
        

    if deleted:
        return JSONResponse(content={"message": "Dosyalar silindi"})
    else:
        return JSONResponse(content={"error": "Dosya bulunamadı"}, status_code=404)