from pathlib import Path

from fastapi.responses import FileResponse

class LocalStorage:
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