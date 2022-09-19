## Getting Started on Windows

### Clone the repository

```bash
cd path/to/project/directory # where you’d like the project to live
git clone https://github.com/zekehuntergreen/comsem.git
```

### Install python3 
Download python3 from https://www.python.org/downloads/. The project is currently at Python 3.10
 
### Install Pipenv
https://pipenv.pypa.io/en/latest/


### Install Pipenv
https://pipenv.pypa.io/en/latest/


### Create virtual environment and install python dependencies from Pipfile.lock

```bash
pipenv install --python 3.10
```


### Install ffmpeg
https://ffmpeg.org/download.html


### Set up local database
Running `make` will copy an sqlite3 database with some minimal test data to `db.sqlite3`. When run in development mode, the Django application will use this database.
```bash
make dev_db
```

### Run the server locally!

```bash
pipenv run python manage.py runserver
```