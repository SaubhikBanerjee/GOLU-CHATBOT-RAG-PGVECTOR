from modules import keywords, phraseto_tsquery, plainto_tsquery, vector_search

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

    # Which of these FTS result present in vector search?
    if len(my_fts_result) > 0:
        most_imp_record = [record[0] for record in result_set4 if record[0] in
                           [r[0] for r in my_fts_result]
                           ]
        final_output = [record[1] for record in result_set4 if record[0] in
                        [r for r in most_imp_record]
                        ]
        print("most_imp_record:", len(most_imp_record))
    print("\033[92mCommon Result(s) \033[0;0m")
    print("\033[92m************************\033[0;0m")
    if len(my_fts_result) > 0:
        for i in final_output:
            print(i)
            print("\033[92m---------------------\033[0;0m")

    print("\033[92m************************\033[0;0m")
    print("\033[38;5;208mSimple Vector Search \033[0;0m")
    print("\033[38;5;208m************************\033[0;0m")
    for i in result_set4:
        print(i[1])
        print("\033[38;5;208m---------------------\033[0;0m")

    print("\033[38;5;208mNormalized Vector Search \033[0;0m")
    print("\033[38;5;208m************************\033[0;0m")
    for i in result_set5:
        print(i[1])
        print("\033[38;5;208m---------------------\033[0;0m")

    print("\033[38;5;208mFull Text Search \033[0;0m")
    print("\033[38;5;208m************************\033[0;0m")
    for i in my_fts_result:
        print(i[1])
        print("\033[38;5;208m---------------------\033[0;0m")
