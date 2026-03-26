from fastapi import FastAPI, UploadFile,File
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse


app = FastAPI()
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

#ana sayfa
@app.get("/")
async def root():
    return FileResponse("static/arayüz.html", media_type="text/html")

#yükleme endpointi
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
   
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
        
        return {"filename": file.filename, "message": "Dosya Yükleme Başarılı!"}
    
        
@app.get("/recordings") #kayıtları listeleme endpointi
async def list_recordings():
    files = os.listdir(UPLOAD_FOLDER)  #uploads klasöründeki dosyaları listele
    recordings = []
    for file in files:
        recordings.append({
            "filename": file,
            "url": f"/audios/{file}"
        })
    return JSONResponse(content=recordings)


@app.get("/audios/{filename}") #kayıtları indirme endpointi
async def get_audio(filename:str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/webm")
    else:
        return JSONResponse(content={"error": "Dosya bulunamadı"}, status_code=404)


@app.delete("/delete/{filename}") #kayıtları silme endpointi
async def delete_audio(filename:str):
    file_location =os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_location):
        os.remove(file_location)
        return JSONResponse(content={"message": "Dosya silindi"})
    else:
        return JSONResponse(content={"error": "Dosya bulunamadı"}, status_code=404)