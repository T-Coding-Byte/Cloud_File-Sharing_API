from connection import engine
from database.models import Base

Base.metadata.create_all(engine)
# psql postgres