from fileinput import filename
from genericpath import exists
from os import name
from storage.local_storage import LocalStorage
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import database.crud as crud

app = FastAPI()
storage = LocalStorage()

@app.get("/")
def root():
    return {"message": "default text"}

@app.get("/health")
def status():
    return{"status": "okay"}

#handle exceptions here
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        name = file.filename
        file_path = Path("uploads") / name
        size = len(contents)

        crud.create_file(name, file_path.suffix, size)
        storage.save(name, contents)
        

        return {"filename": file.filename}
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )


@app.get("/file/{filename}")
def get_file_info(filename:str):
    file = crud.read_file(filename)
    if file is None:
        raise HTTPException(
            status_code=404,
            detail=f"File {filename} not found"
        )

    return {
        "filename": file.filename,
        "category": file.category,
        "size": file.size
    }


@app.put("/file/{filename}")
def update_file(filename, column, newInfo):
    if(column == "filename"):
        storage.rename(filename, newInfo)
    crud.update_file(filename, column, newInfo)
    return {"message": f"{filename} updated successfully"}

@app.delete("/file/{filename}")
def delete_file(filename):

    storage.delete(filename)
    crud.delete_file(filename)
    return {"message": f"{filename} deleted successfully"}











@app.get("/downloads/{filename}")
def download_file(filename: str):
    target_path = storage.get(filename)
    if target_path:
        return FileResponse(target_path)
    else:
        raise HTTPException(status_code=404, detail = f"File {filename} + not found")
    
@app.get("/files")
def get_files():
    return storage.list_files()



#activate uvicorn server:
#uvicorn main:app --reload
