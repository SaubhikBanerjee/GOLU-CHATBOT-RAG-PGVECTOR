# psycopg2 -- for PostgreSQL and pgvector -- for PGVector
# SentenceTransformer -- for Semantic search and cross encoding.
import psycopg2 as pg
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer, CrossEncoder
import itertools

# Good reads: https://www.sbert.net/examples/applications/semantic-search/README.html
#           : https://qdrant.tech/articles/hybrid-search/
#           : https://huggingface.co/cross-encoder
#           : https://www.sbert.net/docs/pretrained_cross-encoders.html


# Function one for FTS
def phraseto_tsquery_v2(query_text, configuration):
    conn = None

    try:

        # Connecting to PostgreSQL cluster.
        conn = pg.connect(
            host="localhost",
            database="postgrdb",
            user="saubhik",
            password="oracle",
            port=54322
        )
        conn.autocommit = True

        # Creating a Cursor
        review_cursor = conn.cursor()
        # The connecting schema, where the table resides
        review_cursor.execute("SET search_path='public'")
        # Registering vector is necessary.
        # This is required only if you are using PGVector
        register_vector(conn)

        # Now building the query text. First I use phraseto_tsquery
        # You can play with the query and user a threshold
        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " phraseto_tsquery(%(configuration)s,%(query_string)s)) rnk" \
                   " from chunk " \
                   " where chunk_fts_doc" \
                   " @@ phraseto_tsquery(%(configuration)s,%(query_string)s)" \
                   " ) x    order by  rnk desc limit 5"
        params = {'query_string': query_text, 'configuration': configuration}

        # Executing the cursor
        review_cursor.execute(sql_text, params)
        # My FTS search results
        sql_result = review_cursor.fetchall()
        conn.close()
        # Return the result set
        return sql_result
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


# Function two for FTS
def plainto_tsquery_v2(query_text, configuration):
    conn = None

    try:

        # Connecting to PostgreSQL cluster.
        conn = pg.connect(
            host="localhost",
            database="postgrdb",
            user="saubhik",
            password="oracle",
            port=54322
        )
        conn.autocommit = True

        # Creating a Cursor
        review_cursor = conn.cursor()
        # The connecting schema, where the table resides
        review_cursor.execute("SET search_path='public'")

        # Registering vector is necessary.
        # This is required only if you are using PGVector
        register_vector(conn)

        # Now building the query text. Now I use plainto_tsquery
        # You can play with the query and user a threshold
        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " plainto_tsquery(%(configuration)s,%(query_string)s)) rnk" \
                   " from chunk " \
                   " where chunk_fts_doc" \
                   " @@ plainto_tsquery(%(configuration)s,%(query_string)s)" \
                   " ) x    order by  rnk desc limit 5"
        params = {'query_string': query_text, 'configuration': configuration}
        review_cursor.execute(sql_text, params)
        sql_result = review_cursor.fetchall()
        conn.close()
        return sql_result
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


# Function for semantic search using PGVector.
# Your semantic search may be little different depending on the vector DB.
def vector_search(query_string):

    # My model which is used for embeddings.
    model = SentenceTransformer('sentence-transformers/msmarco-distilbert-base-v4')
    conn = None
    try:

        # Connecting to PostgreSQL cluster.
        conn = pg.connect(
            host="localhost",
            database="postgrdb",
            user="saubhik",
            password="oracle",
            port=54322
        )
        conn.autocommit = True

        # Creating a Cursor
        review_cursor = conn.cursor()
        review_cursor.execute("SET search_path=public")

        # Registering vector is necessary.
        # This is required only if you are using PGVector
        register_vector(conn)

        # Now getting the query embeddings for the query text.
        query_text = query_string
        query_embeddings = model.encode(query_text)

        # Now building the query text.
        sql_text = "SELECT sectionid, sectiontext FROM chunk " \
                   "WHERE 1=1  " \
                   " and doc_embedding_msmacro IS NOT NULL" \
                   " ORDER BY 1- (doc_embedding_msmacro <=> %(query_embeddings)s) DESC" \
                   " LIMIT 5"
        params = {'query_embeddings': query_embeddings}
        review_cursor.execute(sql_text, params)
        sql_result = review_cursor.fetchall()
        review_cursor.close()
        conn.close()
        return sql_result

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def cross_encoder_rerank(user_query, results):
    # deduplicate - combined result set of FTS and Vector search.
    results = set(itertools.chain(*results))

    """
    Cross-encoder takes a pair of texts and predicts the similarity of them. 
    Unlike embedding models, cross-encoders do not compress text into vector, 
    but uses interactions between individual tokens of both texts. 
    In general, they are more powerful than both BM25 and vector search, 
    but they are also way slower. 
    That makes it feasible to use cross-encoders only for re-ranking of 
    some preselected candidates.
    """
    # re-ranking operation.
    # You might try cross-encoder/ms-marco-MiniLM-L-12-v2
    #               cross-encoder/ms-marco-MiniLM-L-6-v2

    encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    scores = encoder.predict([(user_query, item[1]) for item in results])
    return [v for _, v in sorted(zip(scores, results), reverse=True)]


if __name__ == '__main__':
    query = input("\033[38;5;208mPlease enter the question:\033[0;0m ")

    # Starting FTS
    result_set1 = phraseto_tsquery_v2(query, 'simple')
    result_set2 = phraseto_tsquery_v2(query, 'english')
    result_set3 = plainto_tsquery_v2(query, 'simple')
    result_set4 = plainto_tsquery_v2(query, 'english')

    # Starting semantic search.
    result_set5 = vector_search(query)

    # Total FTS search result
    total_result = [result_set1, result_set2, result_set3, result_set4]
    total_result_non_empty = [x for x in total_result if len(x) > 0]
    if len(total_result_non_empty) > 0:
        # Union to remove duplicates (if any)
        results_union = list(set().union(*total_result_non_empty))
    else:
        results_union = []
    if len(results_union) > 0:
        my_fts_result = list(results_union)
        print("\033[38;5;208mNumber of results in FTS search:\033[0;0m", len(my_fts_result))
        print("*"*40)
    else:
        my_fts_result = []
        print("\033[38;5;208mNothing found on FTS search\033[0;0m")
        print("*" * 40)

    print("\033[38;5;208mNumber of results in Semantic search:\033[0;0m", len(result_set5))
    print("*" * 40)

    # Combining the results of FTS and Semantic search
    combined_result = [my_fts_result, result_set5]
    ranked_results = cross_encoder_rerank(query, combined_result)
    print("\033[38;5;208mNumber of re-ranked results:\033[0;0m", len(ranked_results))
    print("*" * 40)
    print("\033[92mFinal Result(s) \033[0;0m")
    print("\033[92m************************\033[0;0m")
    if len(ranked_results) > 0:
        for i in ranked_results:
            print(i[1])
            print("\033[92m---------------------\033[0;0m")
