from typing import List
import configparser
import eventlet
eventlet.monkey_patch()
import eventlet.wsgi
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from search.elastic_search import connect_to_es, search, fetch_book_id_by_title

app = Flask(__name__)
CORS(app)  # Enable CORS

# Read configuration
config = configparser.ConfigParser()
config.read("config.info")

USERNAME = config.get("DEFAULT", "es_username")
PWD = config.get("DEFAULT", "es_password")
INDEX_NAME = config.get("DEFAULT", "index_name")
ADDED_TERM_REL_WEIGHT = float(config.get("DEFAULT", "added_term_rel_weight"))
FIELDS = config.get("DEFAULT", "fields").split(",")


es = connect_to_es(USERNAME, PWD)

# Sample user data 
user_data = {
    0: {
        "username": "user1",
        "password": "pass1",
        "read_books": [0],
        "liked_books": []
    },
    1: {
        "username": "user2",
        "password": "pass2",
        "read_books": [1],
        "liked_books": []
    }
}


@app.route("/")
def route_index():
    return render_template('index.html')


@app.route("/api/signup", methods=["POST"])
def signup_request():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"error:": "Missing username or password"}), 400
        
        # check if username is already existed
        for user in user_data.values():
            if user["username"] == username:
                return jsonify({"error": "Username already exists"}), 400
        
        new_user_id = max(user_data.keys()) + 1
        user_data[new_user_id] = {
            "username": username,
            "password": password,
            "read_books": [],
            "liked_books": []
        }

        return jsonify({"message": "User registered successfully", "user_id": new_user_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login_request():
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        for user_id, user in user_data.items():
            if user["username"] == username and user["password"] == password:
                return jsonify({"user_id": user_id, "username": username})  # Include username
        
        return jsonify({"error": "Invalid credentials"}), 401

    except KeyError:
        return jsonify({"error": "Missing credentials"}), 400


@app.route("/api/search", methods=["POST"])
def search_request():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id', 0))
        search_query = str(data.get('query', ''))
        selected_genres = data.get('genres', [])  # Get the selected genres from the request
        min_rating = data.get('min_rating', None)  # Get the minimum rating from the request
        min_rating = int(min_rating) if min_rating and int(min_rating) > 0 else None
        query_type = data.get('query_type', 'Ranked Query') # default is Ranked Query
        
        if user_id not in user_data:
            return jsonify({'error': 'Invalid user'}), 400

        read_books = user_data[user_id].get("read_books", [])
        print("user_id: ",user_id, "READ BOOKS:", read_books, "MIN_RATING: ", min_rating, ", Genres: ", selected_genres)
        results = search(
            es=es,
            query_text=search_query,
            index_name=INDEX_NAME,
            relevant_book_ids=read_books,
            fields=FIELDS,
            added_term_rel_weight=ADDED_TERM_REL_WEIGHT,
            genres=selected_genres,  # Pass the selected genres to the search function
            min_rating=min_rating,   # Pass the minimum rating to the search function
            query_type=query_type
        )
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/add_read_book", methods=["POST"])
def add_read_book():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id', 0))
        book_id = data.get('book_id')

        if user_id not in user_data:
            return jsonify({'error': 'Invalid user'}), 400

        if book_id is None:
            return jsonify({'error': 'Missing book_id'}), 400

        # Add the book to the user's read_books list if not already present
        if book_id not in user_data[user_id]["read_books"]:
            user_data[user_id]["read_books"].append(book_id)

        return jsonify({'message': 'Book added to read_books', 'read_books': user_data[user_id]["read_books"]})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/get_read_books", methods=["POST"])
def get_read_books():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id', 0))

        if user_id not in user_data:
            return jsonify({'error': 'Invalid user'}), 400

        read_books = user_data[user_id].get("read_books", [])
        return jsonify({'read_books': read_books})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/get_book_details", methods=["POST"])
def get_book_details():
    try:
        data = request.get_json()
        book_ids = data.get('book_ids', [])

        if not book_ids:
            return jsonify({'error': 'No book IDs provided'}), 400

        # Query Elasticsearch for the book details
        results = []
        for book_id in book_ids:
            response = es.get(index=INDEX_NAME, id=book_id, ignore=[404])
            if response.get('found'):
                results.append(response['_source'])

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
 

@app.route("/api/get_book_id_by_title", methods=["POST"])
def get_book_id_by_title():
    try:
        data = request.get_json()
        title = data.get("title", "")

        if not title:
            return jsonify({"error": "Missing title"}), 400

        book_ids = fetch_book_id_by_title(es, INDEX_NAME, title)
        return jsonify({"book_ids": book_ids})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
  

@app.route("/api/remove_read_book", methods=["POST"])
def remove_read_book():
    try:
        data = request.get_json()
        user_id = int(data.get('user_id', 0))
        book_id = data.get('book_id')

        if user_id not in user_data:
            return jsonify({'error': 'Invalid user'}), 400

        if book_id is None:
            return jsonify({'error': 'Missing book_id'}), 400
        
        if book_id in user_data[user_id]["read_books"]:
            user_data[user_id]["read_books"].remove(book_id)
        
        return jsonify({'message': 'Book removed from read_books', 'read_books': user_data[user_id]["read_books"]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    print("Starting backend server...")
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)