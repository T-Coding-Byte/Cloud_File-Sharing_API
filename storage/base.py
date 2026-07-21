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