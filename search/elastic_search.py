from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser
import math


def relevance_feedback(es, query_text, index_name, doc_ids, fields, added_term_rel_weight):
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
                aggregated_tfidf[term] = aggregated_tfidf.get(term, 0) + tfidf

    sorted_terms = aggregated_tfidf.items()
    multiplier = added_term_rel_weight / (1 - added_term_rel_weight)
    score_sum = sum(aggregated_tfidf.values())
    sorted_terms = [(term, score/score_sum) for term, score in sorted_terms]

    boosted_clauses = [  # Add terms from relevant docs
        {
            "multi_match": {
                "fields": fields,
                "query": term,
                "boost": round(score * multiplier, 2)
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


def search(es: Elasticsearch, query_text: str, index_name: str, relevant_book_ids: list, fields, added_term_rel_weight, genres=None, min_rating=None, query_type="Ranked Query", size=10):
    query = {"bool": {"filter": []}}
    if genres is not None:
        query["bool"]["filter"].append({
                "bool": {
                    "should": [
                        {"match_phrase": {"Genres": genre}} for genre in genres
                    ],
                    "minimum_should_match": 1
                }
            }
        )
    
    if min_rating is not None:
        query["bool"]["filter"].append({"range": {"Rating": {"gte": min_rating}}})
    
    if query_type == "Phrase Query":
        # perform a phrase query
        query["bool"]["must"] = {
            "multi_match": {
                "query": query_text,
                "fields": fields,
                "type": "phrase"
            }
        }
        query = {"query": query}   
    else:
        relevance_query = relevance_feedback(es, query_text, index_name, relevant_book_ids, fields, added_term_rel_weight)
        # merge query with filters into the relevance_query
        if "bool" not in relevance_query["query"]:
            relevance_query["query"]["bool"] = {}
        relevance_query["query"]["bool"]["filter"] = query["bool"]["filter"]
        query = relevance_query
    

    response = es.search(index=index_name, body=query, size=size)
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


def get_title_by_id(es, index_name, id):
    return es.get(index=index_name, id=id)['_source'].get('Title')