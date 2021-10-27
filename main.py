import requests
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel
import pandas as pd
from typing import Optional, List
import numpy as np
from sqlalchemy.orm import Session
from database_config import Base, SessionLocal
from database_config import engine

from database_config import Books_table



app = FastAPI()


Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


response = requests.get('https://www.googleapis.com/books/v1/volumes?q=Hobbit')

google = response.json()

class QueryDetails(BaseModel):
    q: str


@app.get('/')
def welcome():
    return 'Welcome to the books API'


@app.get('/books')
def books(published_date: Optional[int] = None, sort: Optional[str] = None, author_list: Optional[List[str]] = Query(None)):

    book_titles = []
    dates = []
    authors = []

    for value in google['items']:
        book_titles.append(value['volumeInfo']['title'])
        dates.append(value['volumeInfo']['publishedDate'])
        authors.append(value['volumeInfo']['authors'])


    df = pd.DataFrame({'published_date': dates, 'data': google['items'], 'author' : authors})

    df['published_date'] = pd.to_datetime(df['published_date']).dt.year
    

    if sort:

        if sort.startswith('-'):
            df.sort_values(sort[1:], inplace = True, ascending = False)
        else:
            df.sort_values(sort, inplace = True)

    if author_list:

        row_number = df.shape[0]

        final_mask = np.array([False] * row_number)

        for author in author_list:
            mask = [True if author in x else False for x in authors]
            final_mask = np.logical_or(final_mask, mask)

        result = df[final_mask]['data']

        return {'books' : result}


    if published_date:

        result = list(df[df['published_date'] == published_date]['data'])

        return {'books' : result}

    else:
       return {'books': list(df['data'])}

    
@app.get('/books/{book_id}')
def books(book_id: str):

    ids = []

    for value in google['items']:
        ids.append(value['id'])

    df = pd.DataFrame({'book_id': ids, 'data': google['items']})

    result = list(df[df['book_id'] == book_id]['data'])

    if book_id not in ids:
        return {'books' : f'book of id: {book_id} was not found'}

    return {'books' : result}


@app.post("/db")
def download_dataset(details : QueryDetails, db: Session = Depends(get_db)):
    path_to_load = f'https://www.googleapis.com/books/v1/volumes?q={details.q}'

    dataset = requests.get(path_to_load)

    all_books_json = dataset.json()['items']


    for book in all_books_json:
        b_id = book.get('id')
        b_link = book.get('selfLink')
        b_title = book.get('volumeInfo').get('title')
        b_publisheddate = book.get('volumeInfo').get('publishedDate')
        b_language = book.get('volumeInfo').get('language')
        b_maturity = book.get('volumeInfo').get('maturityRating')
    
        new_blog = Books_table(google_id = b_id, link = b_link, title = b_title, publishedDate = b_publisheddate, language = b_language, maturity = b_maturity)

        db.add(new_blog)

        db.commit()

        db.refresh(new_blog)

    return {'Upload successful'}


@app.get('/get_all_data_from_db')
def Get_Data_From_DB(db: Session = Depends(get_db)):
    data = db.query(Books_table).all()
    return data
