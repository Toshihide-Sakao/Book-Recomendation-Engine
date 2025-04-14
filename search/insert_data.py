# Read credentials from the .info file
config = configparser.ConfigParser()
config.read("../config.info")  # Path to your .info file

username = config.get("DEFAULT", "es_username")
password = config.get("DEFAULT", "es_password")

# Connect to Elasticsearch with authentication
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(username, password)
)

# the index name
index_name = "books"

# Function to insert data into Elasticsearch
def insert_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON data from file
        for i, record in enumerate(data):
            try:
                # Insert each record into the Elasticsearch index
                res = es.index(index=index_name, id=i + 1, document=record)
                print(f"Inserted record {i + 1}: {res['result']}")
            except Exception as e:
                print(f"Error inserting record {i + 1}: {e}")


if __name__ == '__main__':
    # Path to the JSON file containing the data
    file_path = "../data/combined_meta_data.json"  

    # Insert data into Elasticsearch
    insert_data(file_path)