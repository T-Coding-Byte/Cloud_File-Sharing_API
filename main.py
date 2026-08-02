import os
from storage.local_storage import LocalStorage
from storage.s3_storage import s3_storage
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import Response
from pathlib import Path
import database.crud as crud
import services.file_service as file_service

if os.getenv("STORAGE_TYPE") == "s3":
    storage = s3_storage()
else:
    storage = LocalStorage()
file_service.sync_storage_and_database(storage)
app = FastAPI()


@app.get("/")
def root():
    return {"message": "default text"}

@app.get("/health")
def status():
    return{"status": "okay"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        name = file.filename
        if crud.file_exists(name):
            raise HTTPException(
                status_code=409,
                detail=f"File '{name}' already exists"
            )

        contents = await file.read()

        
        category = Path(name).suffix
        size = len(contents)

        crud.create_file(name, category, size)
        storage.save(name, contents)
        

        return {"filename": file.filename}

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file"
        )


@app.get("/file/{filename}")
def get_file_info(filename:str):
    try:
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

    except HTTPException:
         raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@app.put("/file/{filename}")
def update_file(filename, column, newInfo):
    allowed_columns = {"filename", "category", "size"}
    if column not in allowed_columns:
         raise HTTPException(
              status_code= 400,
              detail = f"Invalid column '{column}'"
         )

    
    if not crud.file_exists(filename):
        raise HTTPException(
            status_code=404,
            detail=f"File {filename} not found"
        )

    if(column == "filename"):
        if crud.file_exists(newInfo):
                    raise HTTPException(
                        status_code=409,
                        detail=f"File '{newInfo}' already exists"
                    )
        category = crud.read_file(filename).category
        newInfo = f"{newInfo}{category}"
        storage.rename(filename, newInfo)

    if(column == "category"):
        VALID_CATEGORIES = {
            ".pdf",
            ".mp4",
            ".jpg",
            ".jpeg",
            ".png",
            ".txt",
         }
        if newInfo not in VALID_CATEGORIES:
            raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{newInfo}'"
         )
        
    crud.update_file(filename, column, newInfo)
    return {"message": f"{filename} updated successfully"}

@app.delete("/file/{filename}")
def delete_file(filename):

    
    if not crud.file_exists(filename):
         raise HTTPException(
              status_code= 404,
              detail = f"file '{filename}' not found"
         )
    
    storage.delete(filename)
    crud.delete_file(filename)
    return {"message": f"{filename} deleted successfully"}




@app.get("/downloads/{filename}")
def download_file(filename: str):

    file = crud.read_file(filename)
    if file is None:
         raise HTTPException(
              status_code= 404,
              detail = f"file '{filename}' not found"
         )
    contents = storage.get(filename)
    if contents is not None:
        return Response(
        content=contents,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        })
    else:
        raise HTTPException(status_code=404, detail = f"File {filename} + not found")
    
@app.get("/files")
def get_files():
    return storage.list_files()


@app.get("/storage/{storage_type}")
def change_storage(storage_type):
    global storage

    if storage_type == "local":
        newStorage = LocalStorage()
        
    elif storage_type == "s3":
        newStorage = s3_storage()
    else:
        raise HTTPException(
            status_code=400,
            detail="Storage type must be 'local' or 's3'"
        )
    file_service.sync_local_and_s3(storage)
    storage = newStorage
    file_service.sync_storage_and_database(storage)
    return {"message": f"Storage changed to {storage_type}"}



#activate uvicorn server:
#uvicorn main:app --reload
#http://127.0.0.1:8000/docs
if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    url = "http://127.0.0.1:8000/docs"

    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )