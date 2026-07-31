import database.crud as crud
from storage.base import Storage
from pathlib import Path

def sync_storage_and_database(storage : Storage):
    storage_files = storage.list_files()
    database_files = crud.list_files()

    storage_filenames = set(storage_files)
    database_filenames = {file.filename for file in database_files}

    for filename in storage_filenames - database_filenames:
        file_path = Path(filename)
        category = file_path.suffix
        size = storage.get_size(filename)
        crud.create_file(filename, category, size)
        

    for filename in database_filenames - storage_filenames:
        crud.delete_file(filename)
    