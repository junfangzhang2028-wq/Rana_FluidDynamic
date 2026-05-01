#!/bin/bash
(cd backend;
pipenv run python setup.py bdist_wheel --dist-dir=../aq-ui-dist/backend) & (cd frontend;
ng build --prod --aot --build-optimizer --outputPath=../aq-ui-dist/frontend)
git add aq-ui-dist/*
