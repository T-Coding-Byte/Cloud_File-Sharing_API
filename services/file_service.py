import database.crud as crud
from storage.base import Storage
from storage.s3_storage import s3_storage
from storage.local_storage import LocalStorage
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

def sync_local_and_s3(storage: Storage):
    if isinstance(storage, LocalStorage):
        other_storage = s3_storage()
    else:
        other_storage = LocalStorage()

    storage_files = storage.list_files()
    other_files = other_storage.list_files()

    for filename in storage_files:
        if filename not in other_files:
            contents = storage.get(filename)
            other_storage.save(filename, contents)

    for filename in other_files:
        if filename not in storage_files:
            contents = other_storage.get(filename)
            storage.save(filename, contents)

    