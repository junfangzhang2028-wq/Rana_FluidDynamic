#!/bin/bash
(cd backend;
export FLASK_APP=./backend/aqbackend
export FLASK_ENV='development'
source $(pipenv --venv)/bin/activate
flask run -h localhost -p 5000) & (cd frontend;ng serve --port 8000)
kill -- -$$