import requests
from fastapi import FastAPI, Query
import pandas as pd
from typing import Optional, List
import numpy as np



app = FastAPI()

response = requests.get('https://www.googleapis.com/books/v1/volumes?q=Hobbit')

google = response.json()

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


@app.get("/items")
def read_items(q: List[int] = Query(None)):
    return {"q": q}