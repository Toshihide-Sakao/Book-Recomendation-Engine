from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser

app = Flask(__name__, template_folder='HTML templates')


def connect_to_es():
    # Read config.info file to retrive username and password
    config = configparser.ConfigParser()
    config.read("config.info")  # REPLACE to your .info file

    username = config.get("DEFAULT", "username")
    password = config.get("DEFAULT", "password")

    # Connect to Elasticsearch with authentication
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=(username, password)
    )
    return es

# Connect to Elasticsearch
es = connect_to_es()

# Define the home route with a search form
@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query_text = request.form['query']  # Get the query from the form
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,  # query + relevance feedback
                    "fields": ["Title", "Summary", "Author"]
                }
            }
        }
        response = es.search(index="books", body=query)
        results = [hit["_source"] for hit in response["hits"]["hits"]]  # Extract results

    return render_template('search_page.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)