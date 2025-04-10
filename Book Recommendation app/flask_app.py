from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser
from functions import relevance_feedback

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
        
        RELEVANCE = True
        query_text = request.form['query']  # Get the query from the form

        if RELEVANCE:
            index_name = "books"
            doc_ids = [6610, 1347, 420, 2506]  # IDs of relevant documents
            fields = ["Summary", "Author", "Title"]
            top_n_terms = 10  # How many top terms to use in the new query

            query = relevance_feedback(es, query_text, index_name, doc_ids, fields, top_n_terms)
        else:
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