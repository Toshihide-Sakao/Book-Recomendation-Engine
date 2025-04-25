from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser
import math

config = configparser.ConfigParser()
config.read("./config.info")

ADDED_TERM_REL_WEIGHT = float(config.get("DEFAULT", "added_term_rel_weight"))
FIELDS = config.get("DEFAULT", "fields").split(",")


def relevance_feedback(es, query_text, index_name, doc_ids, fields):
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
    multiplier = ADDED_TERM_REL_WEIGHT / (1 - ADDED_TERM_REL_WEIGHT)
    score_sum = sum(aggregated_tfidf.values()) / multiplier
    sorted_terms = [(term, score/score_sum) for term, score in sorted_terms]

    boosted_clauses = [  # Add terms from relevant docs
        {
            "multi_match": {
                "fields": fields,
                "query": term,
                "boost": round(score, 2)
            }
        }
        for term, score in sorted_terms
    ]

    boosted_clauses.append(   # Append actual query terms
        {
            "multi_match": {
                "fields": fields,
                "query": query_text,
                "boost": 1
            }
        }
    )
    
    query_body = {
        "query": {
            "bool": {
                "should": boosted_clauses
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


def search(es: Elasticsearch, query_text: str, index_name: str, relevant_book_ids: list, genres=None, min_rating=None, query_type="Ranked Query"):
    # Initialize the query
    query = {"bool": {"filter": []}}
    # Add genre filtering if genres are provided
    if genres:
        query["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"match_phrase": {"Genres": genre}} for genre in genres
                    ],
                    "minimum_should_match": 1
                }
            }
        )
    
    # Add rating filtering if min_rating is provided
    if min_rating:
        query["bool"]["filter"].append({"range": {"Rating": {"gte": min_rating}}})
    
    if query_type == "Phrase Query":
        # perform a phrase query
        query["bool"]["must"] = {
            "multi_match": {
                "query": query_text,
                "fields": FIELDS,
                "type": "phrase"
            }
        }
        # wrap query in the top-level "query" key
        query = {"query": query}   
    else:
        relevance_query = relevance_feedback(es, query_text, index_name, relevant_book_ids, FIELDS)
        
        # merge query with filters into the relevance_query
        if "bool" not in relevance_query["query"]:
            relevance_query["query"]["bool"] = {}
        relevance_query["query"]["bool"]["filter"] = query["bool"]["filter"]
        query = relevance_query
    

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
