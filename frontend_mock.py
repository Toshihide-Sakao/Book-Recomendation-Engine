import requests
from flask import jsonify

"""
This file contains a number of different mock requests that can be used to test that the server is working properly.
Uncomment the mock request you want to perform.
"""

def flatten_form_data(data):
    flat = []
    for key, value in data.items():
        if isinstance(value, list):
            flat.extend((key, v) for v in value)
        else:
            flat.append((key, value))
    return flat


def search_request_mock():
    url = 'http://localhost:5000/search_request'
    data = {
        'user_id': '0',
        'text_query': 'cool books',
        'settings': ['default']
    }
    payload = flatten_form_data(data)
    response = requests.post(url, data=payload)
    print('Search Request:', response.status_code, response.json())


def add_read_book_request_mock():
    url = 'http://localhost:5000/add_read_book_request'
    data = {
        'user_id': '0',
        'book_id': '1'
    }
    response = requests.post(url, data=data)
    print('Add Read Book:', response.status_code, response.json())


def read_book_list_request_mock():
    url = 'http://localhost:5000/read_book_list_request'
    data = {
        'user_id': '0'
    }
    response = requests.post(url, data=data)
    print('Read Book List:', response.status_code, response.json())


def book_info_request_mock():
    url = 'http://localhost:5000/book_info_request'
    data = {
        'user_id': '0',
        'list_of_book_id': [0, 1]
    }
    payload = flatten_form_data(data)
    response = requests.post(url, data=payload)
    print('Book Info:', response.status_code, response.json())


def rate_book_request_mock():
    url = 'http://localhost:5000/rate_book_request'
    data = {
        'user_id': '0',
        'book_id': '1',
        'user_rating': 'positive'
    }
    response = requests.post(url, data=data)
    print('Rate Book:', response.status_code, response.json())


def login_request_mock():
    url = 'http://localhost:5000/login_requst'
    data = {
        'username': 'bob',
        'password': '123abc'
    }
    response = requests.post(url, data=data)
    print('Login Request:', response.status_code, response.json())


def logout_request_mock():
    url = 'http://localhost:5000/logout_request'
    data = {
        'user_id': 0
    }
    response = requests.post(url, data=data)
    print('Logout Request:', response.status_code, response.json())


if __name__ == "__main__":
    print("Starting frontend mock requests...")
    # Uncomment the mock(s) you'd like to test:
    # search_request_mock()
    # add_read_book_request_mock()
    # read_book_list_request_mock()
    # book_info_request_mock()
    # rate_book_request_mock()
    # login_request_mock()
    logout_request_mock()
