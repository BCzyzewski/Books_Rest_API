from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./books_database.db"

# Create Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create the Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Books_table(Base):
    '''Defining the features of the table that will be created in the database'''

    __tablename__ = "Books"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String)
    link = Column(String)
    title = Column(String)
    publishedDate = Column(String)
    language = Column(String)
    maturity = Column(String)