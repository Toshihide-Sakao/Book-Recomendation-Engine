# Elasticsearch Docker Setup
This project is a search application done as part of the course Search Engines and Information Retrieval Systems DD2477 @ KTH.
The application let's you search for new books to read. It allows you to add books you have read and personalizes the searches accordingly.
Additionally there are search filters for common generes and book rating.

Bellow is a step by step guide how to run the project.


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
3. Create a `config.info` file from the provided template `config_template.info` and fill in your Elasticsearch credentials  
4. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Insert sample data:

   ```bash
   python search/insert_data.py
   ```

---

## 🧪 Running the App

To run the Flask app:

```bash
python main.py
```

---
