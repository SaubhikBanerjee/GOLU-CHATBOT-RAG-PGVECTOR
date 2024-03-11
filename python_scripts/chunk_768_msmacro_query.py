import psycopg2 as pg
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-v4")
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
    imdb_review_cursor = conn.cursor()
    imdb_review_cursor.execute("SET search_path='public'")
    # Registering vector is necessary.
    register_vector(conn)
    # Check the connectivity and check the database version.
    imdb_review_cursor.execute("SELECT version()")
    db_version = imdb_review_cursor.fetchone()
    print("Connected to: ", db_version)
    # Now getting the query embeddings for the query text.
    query_text = input("Query PGVector please!: ")
    query_embeddings = model.encode(query_text)
    sql_text = "SELECT sectionid, sectiontext FROM chunk " \
               "WHERE 1=1  " \
               " and 1=1 " \
               " and doc_embedding_msmacro IS NOT NULL" \
               " ORDER BY 1- (doc_embedding_msmacro <=> %(query_embeddings)s) DESC" \
               " LIMIT 10 "
    params = {'query_embeddings': query_embeddings}
    imdb_review_cursor.execute(sql_text, params)
    sql_result = imdb_review_cursor.fetchall()
    imdb_review_cursor.close()
    # Reopening the cursor for UPDATE.
    imdb_review_cursor = conn.cursor()
    for record in sql_result:
        print("\033[38;5;208mSection Id: \033[0;0m", record[0])
        print("\033[38;5;208mSection Text: \033[0;0m", record[1])

    conn.close()

except Exception as e:
    print(e)
finally:
    if conn is not None:
        conn.close()
