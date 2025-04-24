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

## 🧪 Running the App

To run the Flask app:

```bash
python main.py
```

---
