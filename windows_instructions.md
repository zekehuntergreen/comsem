## Getting Started on Mac

### Clone the repository

```bash
cd path/to/project/directory # where you’d like the project to live
git clone https://github.com/zekehuntergreen/comsem.git
```

### Install python3 
Download python3 from https://www.python.org/downloads/. The project is currently at Python 3.10.7
 
### Create a Python virtual environment
You may need to install the `virtualenv` module first

```bash
pip install virtualenv
```

```bash
mkdir ~/.virtualenvs # or wherever you want virtual environments to live
python3 -m venv ~/.virtualenvs/comsem-env
source ~/.virtualenvs/comsem/Scripts/activate
```

Activate the virtual environment each time you work on the project

```bash
source ~/.virtualenvs/comsem-env/bin/activate
# do stuff
# when finished, deactivate the environment
deactivate
```


### Install ffmpeg
https://ffmpeg.org/download.html


### Set up local database
Running `make` will copy an sqlite3 database with some minimal test data to `db.sqlite3`. When run in development mode, the Django application will use this database.
```bash
make dev_db
```

### Install python dependencies

```bash
# with virtualenv activated
$(comsem-env) cd path/to/project/directory
$(comsem-env) pip install -r requirements.txt
```

### Run the server locally!

```bash
$(comsem-env) python manage.py runserver
```