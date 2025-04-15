# Elasticsearch Docker Setup


## 🚀 Getting Started

To run Elasticsearch locally:

1. **Start Docker Desktop**
2. **Open a terminal**
3. **Run the following command:**

   ```bash
   curl -fsSL https://elastic.co/start-local | sh
   ```

This will download a folder containing a `docker-compose` file and necessary bash scripts, and start the deployment script.

---

## 🧰 Managing the Elasticsearch Container

To start or stop the Elasticsearch container:

1. Navigate to the downloaded folder
2. Run:

   ```bash
   source ./start.sh
   ```

---

## 📚 Insert Data to Index (One-Time Setup)

1. Visit the Elasticsearch web interface at: [http://localhost:5601](http://localhost:5601)
2. Create an index named `books`
3. Create a `config.info` file and fill in your Elasticsearch credentials  
   (use the provided template in the repo)
4. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Insert sample data:

   ```bash
   python search/insert_data.py
   ```

---

## 🧪 Running the Program

To run the Flask backend with the mock program:

```bash
python start.py
```

---

## 🔧 TODO

- Add instructions for running the complete `flask_app`

---

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
