from fileinput import filename
from genericpath import exists
from os import name
from storage.local_storage import LocalStorage
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()
items = []
storage = LocalStorage()

@app.get("/")
def root():
    return {"message": "default text"}

@app.get("/health")
def status():
    return{"status": "okay"}

@app.post("/items")
def create_item(item: str):
    items.append(item)
    return item

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    storage.save(file.filename, contents)
    return {"filename": file.filename}

@app.get("/downloads/{filename}")
def download_file(filename: str):
    target_path = storage.get(filename)
    if target_path:
        return FileResponse(target_path)
    else:
        raise HTTPException(status_code=404, detail = "File {filename} + not found")
    
@app.get("/files")
def get_files():
    target_path = Path("uploads")
    files = []
    for file in target_path.iterdir():
        files.append(file.name)
    return files

@app.get("/items")
def get_items():
    return items

#activate uvicorn server:
#uvicorn main:app --reload
