from abc import ABC, abstractmethod

class Storage(ABC):
    


    @abstractmethod
    def save(self, filename, contents):
        pass

    @abstractmethod
    def get(self, filename):
        pass

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def delete(self, filename):
        pass

    @abstractmethod
    def rename(self, old_name, new_name):
        pass