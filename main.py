import os
from authentication.jwt import create_access_token
from storage.local_storage import LocalStorage
from storage.s3_storage import s3_storage
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.responses import Response
from pathlib import Path
import database.crud as crud
import services.file_service as file_service
from contextlib import asynccontextmanager
from authentication.auth import hash_password, verify_password
from authentication.schemas import loginRequest, passwordSetup, PasswordReset
from authentication.dependancies import get_current_user
from database.connection import engine
from database.models import Base

Base.metadata.create_all(bind=engine)
RESET_KEY = os.getenv("PASSWORD_RESET_KEY")

if os.getenv("STORAGE_TYPE") == "s3":
    storage = s3_storage()
else:
    storage = LocalStorage()
file_service.sync_storage_and_database(storage)


app = FastAPI()


@app.get("/")
def root():
    return {"message": "API running. To access the UI, use the Swagger docs available at http://localhost:8000/docs"}



@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user = Depends(get_current_user)):
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
def get_file_info(filename:str, user = Depends(get_current_user)):
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
def update_file(filename, column, newInfo, user = Depends(get_current_user)):
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
def delete_file(filename, user = Depends(get_current_user)):

    
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
def get_files(user = Depends(get_current_user)):
    return storage.list_files()


@app.get("/storage/{storage_type}")
def change_storage(storage_type, user = Depends(get_current_user)):
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

###authentication
@app.post("/auth/setup")
def setup_password(data: passwordSetup):
    user = crud.read_user()
    if user is not None:
        raise HTTPException(status_code=400, detail = 'User has already been crated')
    password_hash = hash_password(data.password)

    crud.create_user(password_hash)
    return {
        "message": "User created successfully"
    }

@app.post("/auth/login")
def login(data: loginRequest):
    user = crud.read_user()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    access_token = create_access_token(data = {"sub":str(user.id)})
    return {
    "access_token": access_token,
    "token_type": "bearer"

}

@app.get("/protected")
def protected_route(
    user = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user": user
    }

@app.post("/auth/reset-password")
def reset_password(data: PasswordReset):
    if data.reset_key != RESET_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid reset key"
        )

    password_hash = hash_password(data.new_password)

    crud.update_password(password_hash)

    return {
        "message": "Password reset successful"
    }


#activate uvicorn server:
#uvicorn main:app --reload
#http://127.0.0.1:8000/docs

#   if __name__ == "__main__":
 #       import uvicorn
  #      import webbrowser
   #     import threading
#
 #       url = "http://127.0.0.1:8000/docs"

 #       threading.Timer(1.0, lambda: webbrowser.open(url)).start()
#
 #       uvicorn.run(
  #          "main:app",
   #         host="127.0.0.1",
    #        port=8000,
     #      reload=True
      #  )
##