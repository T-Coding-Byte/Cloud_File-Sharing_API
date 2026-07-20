from fileinput import filename
from genericpath import exists
from os import name
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
app = FastAPI()
items = []

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
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    with open(upload_dir / file.filename, "wb") as target:
        target.write(contents)

    return {"filename": file.filename}

@app.get("/downloads/{filename}")
def download_file(filename: str):
    target_path = Path("uploads") / filename
    if target_path.exists():
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
