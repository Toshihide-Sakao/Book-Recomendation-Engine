from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser
import math


def relevance_feedback(es, query_text, index_name, doc_ids, fields, added_term_weight=0.01, query_term_weight=4, genres=None, min_rating=None):
    aggregated_tfidf = {}
    
    for doc_id in doc_ids:
        term_vector_response = es.termvectors(
            index=index_name,
            id=doc_id,
            fields=fields,
            term_statistics=True
        )
        
        term_vectors = term_vector_response.get("term_vectors", {})
        for field_name, field_data in term_vectors.items():
            terms_data = field_data.get("terms", {})
            for term, stats in terms_data.items():
                # Get term frequency and document frequency
                tf = stats.get("term_freq", 0)
                df = stats.get("doc_freq", 1)
                
                doc_count = es.count(index=index_name)["count"]
                idf = math.log((doc_count + 1) / (df + 1)) + 1
                
                tfidf = tf * idf
                
                # TODO: is this correct?: Aggregate the TF-IDF scores if the same term appears across different fields/docs.
                aggregated_tfidf[term] = aggregated_tfidf.get(term, 0) + tfidf

    # sorted_terms = sorted(aggregated_tfidf.items(), key=lambda x: x[1], reverse=True)[:top_n_terms]
    sorted_terms = aggregated_tfidf.items()

    boosted_clauses = [  # Add terms from relevant docs
        {
            "multi_match": {
                "fields": fields,
                "query": term,
                "boost": round(score, 2) * added_term_weight
            }
        }
        for term, score in sorted_terms
    ]

    boosted_clauses.append(   # Append actual query terms
        {
            "multi_match": {
                "fields": fields,
                "query": query_text,
                "boost": query_term_weight
            }
        }
    )
    excluding_filter = list()
    if genres:  # assume genres is a list like ["Action", "Drama"]
        excluding_filter.append(
            {
                "bool": {
                    "should": [
                        {"match_phrase": {"Genres": genre}} for genre in genres
                    ],
                    "minimum_should_match": 1
                }
            }
        )

    if min_rating:
        excluding_filter.append(
            {
                    "range": {
                        "Rating": { "gte": min_rating }
                    }
                }
            )


    query_body = {
        "query": {
            "bool": {
                "should": boosted_clauses,
                "filter": excluding_filter
            }
        }
    }
    return query_body


def connect_to_es(username, password):
    # Connect to Elasticsearch with authentication
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=(username, password)
    )
    return es


def search(es: Elasticsearch, query_text: str, index_name:str, relevant_book_ids:list, personalization=True, genres=None, min_rating=None):
    results = []
    fields = ["Summary", "Author", "Title", "Genres"]

    if personalization:
        query = relevance_feedback(
            es, 
            query_text, 
            index_name, 
            relevant_book_ids, 
            fields,  
            added_term_weight=0.01, 
            query_term_weight=4, 
            genres=genres, 
            min_rating=min_rating
            )
    else:
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["Title", "Summary", "Author", "Genres"]
                }
            }
        }
    response = es.search(index=index_name, body=query)
    results = [hit["_source"] for hit in response["hits"]["hits"]]  # Extract results

    return results


def fetch_book_id_by_title(es, index_name, title):
    query = {
        "query": {
            "match": {
                "Title": title  # Match the Title field
            }
        }
    }

    response = es.search(index=index_name, body=query)
    if response["hits"]["total"]["value"] > 0:
        for hit in response["hits"]["hits"]:
            print(f"Found Book - ID: {hit['_id']}, Title: {hit['_source'].get('Title', 'N/A')}")
        return [hit["_id"] for hit in response["hits"]["hits"]]  # Return a list of matching book IDs
    else:
        print("No book found with the given Title.")
        return []
