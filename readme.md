# Frontend backend mock

This project aims to create a basic demonstration for how to setup a backend in flask

There is also a basic frontend mock, to test sending requests to the backend. There are already a number of dummy requests to try.

Go to frontend_mock.py and uncomment the tests that you would like to run

Feel free to use the backend_template.py as a starting point when setting up the actual server

## Running the project

Just run the start.py file

it will:

1. Create a new virtual python environment in \<Current directory\>/venv/
2. Install all the necesssary pip requirements in the newly created virtual environment
3. Launch backend_template.py as a subprocess
4. Launch frontend_mock.py as a subprocess

You can also just run the backend_template.py or the frontend_mock.py files individually,
but using the start.py script is the easiest way
