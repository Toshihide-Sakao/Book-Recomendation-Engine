from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import configparser
import math


def relevance_feedback(es, query_text, index_name, doc_ids, fields, top_n_terms, added_term_weight=0.01, query_term_weight=4):
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
                
                doc_count = 10000  # TODO: move out constant
                idf = math.log((doc_count + 1) / (df + 1)) + 1
                
                tfidf = tf * idf
                
                # TODO: is this correct?: Aggregate the TF-IDF scores if the same term appears across different fields/docs.
                aggregated_tfidf[term] = aggregated_tfidf.get(term, 0) + tfidf

    sorted_terms = sorted(aggregated_tfidf.items(), key=lambda x: x[1], reverse=True)[:top_n_terms]

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

def search(es: Elasticsearch, query_text: str, index_name:str, relevant_book_ids:list, personanlization=True):
    results = []
    fields = ["Summary", "Author", "Title"]
    top_n_terms = 10  # How many top terms to use in the new query

    if personanlization:
        query = relevance_feedback(es, query_text, index_name, relevant_book_ids, fields, top_n_terms)
    else:
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["Title", "Summary", "Author"]
                }
            }
        }
    response = es.search(index=index_name, body=query)
    results = [hit["_source"] for hit in response["hits"]["hits"]]  # Extract results

    return results

if __name__ == '__main__':
    print("starting")
    res = search(es, "chicken", "books", [], False)
    print(res)