from search.elastic_search import search, get_title_by_id, connect_to_es
import configparser
import numpy as np

config = configparser.ConfigParser()
config.read("config.info")

USERNAME = config.get("DEFAULT", "es_username")
PWD = config.get("DEFAULT", "es_password")
INDEX_NAME = config.get("DEFAULT", "index_name")

es = connect_to_es(USERNAME, PWD)

paramsets = [{
	"fields": ["Summary","Author","Title","Genres"],
	"added_term_rel_weight": 0.10
},
{
	"fields": ["Summary","Author","Title","Genres"],
	"added_term_rel_weight": 0.30
},{
	"fields": ["Summary","Author","Title","Genres"],
	"added_term_rel_weight": 0.50
},{
	"fields": ["Summary","Author","Title","Genres"],
	"added_term_rel_weight": 0.70
},{
	"fields": ["Summary","Author","Title","Genres"],
	"added_term_rel_weight": 0.90
},{
	"fields": ["Summary","Author","Title","Genres^2"],
	"added_term_rel_weight": 0.10
},
{
	"fields": ["Summary","Author","Title","Genres^2"],
	"added_term_rel_weight": 0.30
},{
	"fields": ["Summary","Author","Title","Genres^2"],
	"added_term_rel_weight": 0.50
},{
	"fields": ["Summary","Author","Title","Genres^2"],
	"added_term_rel_weight": 0.70
},{
	"fields": ["Summary","Author","Title","Genres^2"],
	"added_term_rel_weight": 0.90
},
{
	"fields": ["Summary","Author","Title^2","Genres"],
	"added_term_rel_weight": 0.10
},
{
	"fields": ["Summary","Author","Title^2","Genres"],
	"added_term_rel_weight": 0.30
},{
	"fields": ["Summary","Author","Title^2","Genres"],
	"added_term_rel_weight": 0.50
},{
	"fields": ["Summary","Author","Title^2","Genres"],
	"added_term_rel_weight": 0.70
},{
	"fields": ["Summary","Author","Title^2","Genres"],
	"added_term_rel_weight": 0.90
},{
	"fields": ["Summary","Author","Title^3","Genres^2"],
	"added_term_rel_weight": 0.10
},
{
	"fields": ["Summary","Author","Title^3","Genres^2"],
	"added_term_rel_weight": 0.30
},{
	"fields": ["Summary","Author","Title^3","Genres^2"],
	"added_term_rel_weight": 0.50
},{
	"fields": ["Summary","Author","Title^3","Genres^2"],
	"added_term_rel_weight": 0.70
},{
	"fields": ["Summary","Author","Title^3","Genres^2"],
	"added_term_rel_weight": 0.90
},
]

book_relevance = {}



def DCG(results):
	relevance_scores = [np.array(book_relevance[title], dtype=float) for title in results]
	k = len(relevance_scores)
	return np.sum(relevance_scores[:k] / np.log2(np.arange(2, k + 2)))

def nDCG(results, k):
	relevance_scores = [np.array(book_relevance[title], dtype=float) for title in results]
	dcg = np.sum((np.power(2, relevance_scores[:k])-1) / np.log2(np.arange(2, k + 2)))
	idcg = np.sum((np.power(2, sorted(relevance_scores, reverse=True)[:k] )-1)/ np.log2(np.arange(2, k + 2)))
	return dcg / idcg if idcg > 0 else 0.0

def main():
	unique_titles = set()
	QUERY_TEXT = "Turkish Novels"
	RELEVANT_BOOKS = "7097;2479;992"

	print(f"query_text: {QUERY_TEXT}")
	book_ids = [int(book_id) for book_id in RELEVANT_BOOKS.split(";")]
	print("relevant books:", [get_title_by_id(es, INDEX_NAME, book_id) for book_id in book_ids])
	for index, params in enumerate(paramsets):

		results = search(
			es=es,
			query_text=QUERY_TEXT,
			index_name=INDEX_NAME,
			relevant_book_ids=book_ids,
			fields=params['fields'],
			added_term_rel_weight=params['added_term_rel_weight'],
			genres=[],  # Pass the selected genres to the search function
			min_rating=0,   # Pass the minimum rating to the search function
			query_type="Ranked Query"
		)
		#print(f"results {index}:", [{"title": r['Title'], "author": r['Author']} for r in results])
		[unique_titles.add(r['Title']) for r in results]
		#print("NDCG:", nDCG([r['Title'] for r in results], 5))
		#for r in results:
	#		print(r['Title']) 
	#	print("\n ========================================== \n")


def run_one_paramset():
	REL_WEIGHT = 0.3
	FIELDS = ["Summary","Author","Title^3","Genres^2"]
	QUERY_TEXT = "Turkish Novels"
	RELEVANT_BOOKS = "7097;2479;992"

	unique_titles = set()
	print(f"query_text: {QUERY_TEXT}")
	book_ids = [int(book_id) for book_id in RELEVANT_BOOKS.split(";")]
	print("relevant books:", [get_title_by_id(es, INDEX_NAME, book_id) for book_id in book_ids])
	
	results = search(
		es=es,
		query_text=QUERY_TEXT,
		index_name=INDEX_NAME,
		relevant_book_ids=book_ids,
		fields=FIELDS,
		added_term_rel_weight=REL_WEIGHT,
		genres=[],  # Pass the selected genres to the search function
		min_rating=0,   # Pass the minimum rating to the search function
		query_type="Ranked Query",
		size=100
	)
	print(f"results:", [{"title": r['Title'], "author": r['Author']} for r in results[:10]])
	[unique_titles.add(r['Title']) for r in results]
	#print("NDCG:", nDCG([r['Title'] for r in results], 10))

	print("unique titles:", unique_titles)
if __name__ == '__main__':
	#main()
	run_one_paramset()
