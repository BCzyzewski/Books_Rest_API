## Welcome to the Books REST API repository

API is running here:



#### Basic information
This repository contains the source files for the REST API storing information about books from Google. Project was bulid using the FastAPI Python framework which allows to create light-weight, modern and advanced REST APIs.

#### API capabilities
<b>Please use /docs to get to Swagger UI.</b>

<b>GET methods</b>
/books - show all of the books from https://www.googleapis.com/books/v1/volumes?q=Hobbit
/books?published_data - filter the books by the published date <i>(example /books?publised_date=1995)</i>
/books?sort - sort the books by the published_date, use "-" sign to sort descending <i>(example /books?sort=-published_date)</i>
/books?author - filter the books by the author <i>(example /books?author='Jan Kowalski'&author='Anna Kowalska')</i>

/books/<book_id> - show a book of a chosen id

<b>POST methods</b>
/db - downloading data from z https://www.googleapis.com/books/v1/volumes?q={variable} and loading it into database.
