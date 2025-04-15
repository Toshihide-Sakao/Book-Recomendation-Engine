# This is a backend template for how to setup a flask server
from typing import List
import configparser
import eventlet
eventlet.monkey_patch()  # Avoid warning about wsgi server for production
import eventlet.wsgi
from search.elastic_search import connect_to_es, search

from flask import Flask, request, jsonify

app = Flask(__name__)

# Read config.info file to retrive username and password
config = configparser.ConfigParser()
config.read("config.info")  # REPLACE to your .info file

USERNAME = config.get("DEFAULT", "es_username")
PWD = config.get("DEFAULT", "es_password")
INDEX_NAME = config.get("DEFAULT", "index_name")

es = connect_to_es(USERNAME, PWD)

book_data = {
    0: {
        "book_name": "the best book ever",
        "author": "some guy",
        "page_count": 42,
        "genres": ["history", "religion"],
        "description": ["the book with all the answers"]
    },
    1: {
        "book_name": "the best book ever2",
        "author": "some guy2",
        "page_count": 42,
        "genres": ["history", "religion", "art"],
        "description": ["the book with all the answers2"]
    },
}

user_data = {
    0: {
        "username": "bob",
        "password": "123abc",
        "read_books": [0, 1]
    },
    1: {
        "username": "alice",
        "password": "123abcd",
        "read_books": [1]
    }
}


@app.route("/")
def route_index():
    return "<p>add homepage html here!</p>", 200


@app.route("/home")
def route_home():
    return "<p>add homepage html here!</p>", 200


@app.route('/search_request', methods=['POST', 'GET'])
def search_request():
    try:
        print("request:", request.form)
        user_id: int = int(request.form['user_id'])
        search_query: str = str(request.form['text_query']) # What the user has typed in the search bar
        settings: List[str] = request.form.getlist(request.form['settings']) # Additional settings that the user has selected
        if not all(isinstance(s, str) for s in settings):
            return jsonify({'error': 'All settings must be strings'}), 400
        
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400

    ranked_book_id_list = list()

    if user_id in user_data.keys():

        read_books = user_data.get(user_id).get("read_books", list())

        ranked_book_id_list = search(
            es=es,
            query_text=search_query,
            index_name=INDEX_NAME, 
            relevant_book_ids=read_books, 
            personanlization=True,
            genre="Magic",  #settings.get("genre"),
            min_rating=4.0  #setting.get("min_rating")
            )
    else:
        return jsonify({'error': f'Invalid user_id: {str(e)}'}), 400


    return jsonify({"response": ranked_book_id_list}), 200


@app.route('/add_read_book_request', methods=['POST', 'GET'])
def add_read_book_request():
    try:
        print("request:", request.form)
        user_id: int = int(request.form['user_id'])
        book_id: int = int(request.form['book_id'])
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    # ADD YOUR CODE HERE
    if not book_id in book_data.keys():
        return jsonify({'error': f'Invalid book id'}), 400
    
    if not user_id in user_data.keys():
        return jsonify({'error': f'Invalid user id'}), 400

    # Add it to the books that the user has read
    if not book_id in user_data[user_id]["read_books"]:
        user_data[user_id]["read_books"].append(book_id)

    return jsonify({'success': True}), 200


@app.route('/read_book_list_request', methods=['POST', 'GET'])
def read_book_list_request():
    try:
        print("request:", request.form)
        user_id: int = int(request.form['user_id'])
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    # ADD YOUR CODE HERE
    
    if not user_id in user_data.keys():
        return jsonify({'error': f'Invalid user id'}), 400

    # return the list of books that the user has read
    read_books = user_data[user_id]["read_books"]

    return jsonify({"response": read_books}), 200


@app.route('/book_info_request', methods=['POST', 'GET'])
def book_info_request():
    try:
        print("request:", request.form)
        user_id: int = int(request.form['user_id'])
        raw_list_of_book_id: list = request.form.getlist('list_of_book_id')
        list_of_book_id: List[int] = list()
        for book_id in raw_list_of_book_id:
            list_of_book_id.append(int(book_id))
        
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    # ADD YOUR CODE HERE

    if not user_id in user_data.keys():
        return jsonify({'error': f'Invalid user id'}), 400

    # return the list of books that the user has read
    list_of_book_info = []
    for book_id in list_of_book_id:
        if not book_id in book_data.keys():
            return jsonify({'error': f'Invalid bookid: {str(book_id)}'}), 400
        
        book_info = book_data[book_id]
        list_of_book_info.append(book_info)

    return jsonify({"response": list_of_book_info}), 200


@app.route('/rate_book_request', methods=['POST', 'GET'])
def rate_book_request():
    try:
        print("request:", request.form)
        user_id: int = int(request.form['user_id'])
        book_id: int = int(request.form['book_id'])
        user_rating: str = str(request.form['user_rating'])

        if not user_rating in ["neutral", "positive"]:
            return jsonify({'error': f'Invalid user rating: {user_rating}'}), 400

    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    # ADD YOUR CODE HERE
    if not book_id in book_data.keys():
        return jsonify({'error': f'Invalid bookid: {str(book_id)}'}), 400
    
    if not user_id in user_data.keys():
        return jsonify({'error': f'Invalid user id'}), 400

    # Make sure the book is registered as read
    if not book_id in user_data[user_id]["read_books"]:
        user_data[user_id]["read_books"].append(book_id)

    if user_rating == "positive":
        if not book_id in user_data[user_id]["liked_books"]:
            user_data[user_id]["liked_books"].append(book_id)

    return jsonify({'success': True}), 200


@app.route('/login_requst', methods=['POST', 'GET'])
def login_request():
    try:
        print("request:", request.form)
        username: str = str(request.form['username'])
        password: str = str(request.form['password'])
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    # ADD YOUR CODE HERE
    # handle user login and get user id

    user_id = 0
    return jsonify({"response": user_id}), 200


@app.route('/logout_request', methods=['POST', 'GET'])
def logout_request():
    try:
        print("request:", request.form)
        user_id: int = request.form['user_id']
    except (ValueError, KeyError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    return jsonify({'success': True}), 200


if __name__ == "__main__":
    print("Starting backend")
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
    # Flask.run(app, port=5000)






        
