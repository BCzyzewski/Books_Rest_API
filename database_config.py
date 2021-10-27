from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./books_database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Books_table(Base):

    __tablename__ = "Books"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String)
    link = Column(String)
    title = Column(String)
    publishedDate = Column(String)
    language = Column(String)
    maturity = Column(String)
    

    # items = relationship("Item", back_populates="owner")

# class Item(Base):

#     __tablename__ = "items"


#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("Blog_Build", back_populates="items")


Base.metadata.create_all(engine)
