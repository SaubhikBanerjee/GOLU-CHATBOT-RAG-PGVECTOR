from modules import keywords, phraseto_tsquery, plainto_tsquery, vector_search
from sentence_transformers import CrossEncoder
import itertools


def rerank(_query, results):
    # deduplicate
    results = set(itertools.chain(*results))

    # re-rank
    encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    scores = encoder.predict([(_query, item[1]) for item in results])
    return [v for _, v in sorted(zip(scores, results), reverse=True)]


if __name__ == '__main__':
    query = input("Please enter the question: ")

    # We are creating 5 results sets for the question.
    normalized_query = (' '.join(keywords(query))).strip()

    # Starting FTS
    result_set1 = phraseto_tsquery(query)
    result_set2 = phraseto_tsquery(normalized_query)
    result_set3 = plainto_tsquery(query)
    result_set6 = plainto_tsquery(normalized_query)

    # Starting semantic search.
    result_set4 = vector_search(query)
    result_set5 = vector_search(normalized_query)

    print("result_set1:", len(result_set1))
    print("result_set2:", len(result_set2))
    print("result_set3:", len(result_set3))
    print("result_set6:", len(result_set6))
    print("result_set4:", len(result_set4))
    print("result_set5:", len(result_set5))
    # most important FTS records by union
    total_result = [result_set1, result_set2, result_set3, result_set6]
    total_result_non_empty = [x for x in total_result if len(x) > 0]
    if len(total_result_non_empty) > 0:
        results_union = list(set().union(*total_result_non_empty))
    else:
        results_union = []
    if len(results_union) > 0:
        my_fts_result = list(results_union)
        print("my_fts_result:", len(my_fts_result))
    else:
        my_fts_result = []
    combined_result=[my_fts_result, result_set4, result_set5 ]
    ranked_results = rerank(query, combined_result)
    print(ranked_results)

