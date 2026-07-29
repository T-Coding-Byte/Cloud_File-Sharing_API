from pathlib import Path
from .base import Storage #potential issue, solve via from base import Storage


class LocalStorage(Storage):
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def save(self, filename, contents):
        with open(self.upload_dir / filename, "wb") as target:
            target.write(contents)
        return filename
    
    def get(self, filename):
        file_path = self.upload_dir / filename

        if file_path.exists():
            return file_path
        return None
    
    def list_files(self):
        content = []
        for file in self.upload_dir.iterdir():
            content.append(file.name)
        return content

    def delete(self, filename):
        file_path = Path("uploads") / filename

        if file_path.exists():
            file_path.unlink()

    def rename(self, old_name, new_name):
        old_path = Path("uploads") / old_name
        new_path = Path("uploads") / new_name

        old_path.rename(new_path)