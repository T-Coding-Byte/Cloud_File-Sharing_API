from database.connection import engine, SessionFactory
from database.models import Base, File
from sqlalchemy import Delete, insert, select, delete



def create_file(file_name, file_category, file_size):
    with SessionFactory() as session:
        session.execute(insert(File).values(
            filename = file_name, 
            category = file_category, 
            size = file_size
            ))
        session.commit()

def read_file(file_name): #replace parameter with file path if needed
    with SessionFactory() as session:
        file = session.execute(select(File).where(File.filename == file_name)).scalar()
        if file is None:
            return None
        
        return file

def update_file(file_name, column, new_info):
    with SessionFactory() as session:
        file = session.execute(select(File).where(File.filename == file_name)).scalar()

        if file is None:
            return None

        if column == "filename":
            file.filename = new_info
        elif column == "category":
            file.category = new_info
        elif column == "size":
            file.size = new_info
        session.commit()

def delete_file(file_name):
    with SessionFactory() as session:
        session.execute(delete(File).where(File.filename == file_name))
        session.commit()


def file_exists(file_name):
    with SessionFactory() as session:
        file = session.execute(
            select(File).where(File.filename == file_name)
        ).scalar_one_or_none()

        return file is not None

def list_files():
    with SessionFactory() as session:
        files = session.execute(select(File)).scalars().all()
        
        return files



