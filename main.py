import requests
import numpy as np
import pandas as pd

# FastAPI dependencies
from fastapi import FastAPI, Query, Depends
from typing import Optional, List
from pydantic import BaseModel

# SQLAlchemy dependencies
from sqlalchemy.orm import Session

# Database Configuration files dependencies
from database_config import Base, SessionLocal
from database_config import engine
from database_config import Books_table

# Create the FastAPI app and a table in the database
app = FastAPI()

Base.metadata.create_all(engine)


def get_db():
    '''Allowing to create a session for the database'''
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Downloading the data of the Google API service
response = requests.get('https://www.googleapis.com/books/v1/volumes?q=Hobbit')

json_data_books = response.json()


@app.get('/')
def welcome():
    '''Welcoming and presenting API features to the user'''

    message = 'Welcome to the books REST API. This API was created using the FastAPI python framework. Source code and documentation can be found here: https://github.com/BCzyzewski/Books_Rest_API. Please use the /docs for the Swagger UI.'

    return message


@app.get('/books')
def show_books(published_date: Optional[int] = None, sort: Optional[str] = None, author_list: Optional[List[str]] = Query(None)):
    '''Returns all of the Hobbit books based on optional conditions.

    Accepts parameters:

    publised_date = show books only for the choosen year (example /books?publised_date=1995)

    sort = sorts based on published_date. Insert "-" for descending sorting (example /books?sort=published_date)

    author_list = accepts any number of authors, shows only books written by those authors (exaple /books?author='Jan Kowalski'&author='Anna Kowalska')
    '''

    # Initialize lists that will be storing book features
    book_titles = []
    dates = []
    authors = []


    # Get book features
    for value in json_data_books['items']:
        book_titles.append(value['volumeInfo']['title'])
        dates.append(value['volumeInfo']['publishedDate'])
        authors.append(value['volumeInfo']['authors'])

    # Create a pandas Dataframe that wille help with sorting and filtering
    df = pd.DataFrame({'published_date': dates, 'data': json_data_books['items'], 'author' : authors})

    df['published_date'] = pd.to_datetime(df['published_date']).dt.year
    
    # Sort values if the sort parameter is passed.
    if sort:

        if sort.startswith('-'):
            df.sort_values(sort[1:], inplace = True, ascending = False)
        else:
            df.sort_values(sort, inplace = True)

    # Filter for passed authors.
    if author_list:

        row_number = df.shape[0]

        # Create a mask that will be used for filtering the DataFrame
        final_mask = np.array([False] * row_number)

        for author in author_list:
            mask = [True if author in x else False for x in authors]
            final_mask = np.logical_or(final_mask, mask)

        result = df[final_mask]['data']

        return {'books' : result}

    # Filter for books of choosen publised date (only year)
    if published_date:

        result = list(df[df['published_date'] == published_date]['data'])

        return {'books' : result}

    else:

        # Return all of the books if no parameter is passed
       return {'books': list(df['data'])}

    
@app.get('/books/{book_id}')
def show_books_ID(book_id: str):
    '''Return a book of a choosen id'''

    # Store all of the ids
    ids = []

    for value in json_data_books['items']:
        ids.append(value['id'])

    # Create a DataFrame that will help with filtering
    df = pd.DataFrame({'book_id': ids, 'data': json_data_books['items']})

    result = list(df[df['book_id'] == book_id]['data'])

    # If the id was not found display a proper message
    if book_id not in ids:
        return {'books' : f'book of id: {book_id} was not found'}

    return {'books' : result}


class QueryDetails(BaseModel):
    '''Class used for the post route. It allows to pass information that will be used by the API'''
    q: str


@app.post("/db")
def Download_Data_To_db(details : QueryDetails, db: Session = Depends(get_db)):
    '''Updates the database with information about the books from the Google API. After passing the q parameter it stores books with the q string in the title.'''

    # Get JSON data about the books
    path_to_load = f'https://www.googleapis.com/books/v1/volumes?q={details.q}'

    dataset = requests.get(path_to_load)

    all_books_json = dataset.json()['items']


    # Update the database with choosen features of the books
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

    return {'Result' : f'Upload successful to database with {len(all_books_json)} rows added'}


@app.get('/get_all_data_from_db')
def Get_Data_From_DB(db: Session = Depends(get_db)):
    '''Returns all of the rows stored in the database.'''

    data = db.query(Books_table).all()
    return data
