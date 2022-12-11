# Set-Up

## Environment Requirements

  - python >= 3.10.9

## Create a python virtual environment

- switch to the working directory where the project is located

- `python -m venv venv`
- activate the environment `.\venv\Scripts\activate`
- install dependencies `pip install -r .\requirements.txt`

## Start the Server

execute `python .\manage.py runserver 0.0.0.0:8000`, then open `localhost:8000` in your browser, you can see the app.
