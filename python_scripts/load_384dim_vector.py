import psycopg2 as pg
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

model = SentenceTransformer("all-MiniLM-L6-v2")
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
    chunk_cursor = conn.cursor()
    chunk_cursor.execute("SET search_path=public")
    # Registering vector is necessary.
    register_vector(conn)
    # Check the connectivity and check the database version.
    chunk_cursor.execute("SELECT version()")
    db_version = chunk_cursor.fetchone()
    print("Connected to: ", db_version)
    # Now creating a cursor to get the 50k IMDB movie review.
    chunk_cursor.execute("SELECT sectionid, sectiontext FROM chunk "
                         "WHERE doc_embedding IS NULL")
    sql_result = chunk_cursor.fetchall()
    chunk_cursor.close()
    # Reopening the cursor for UPDATE.
    chunk_cursor = conn.cursor()
    for record in sql_result:
        print("sectionid: ", record[0])
        # Sentences are encoded by calling model.encode()
        embeddings = model.encode(record[1])
        print(len(embeddings))

        update_statement = "UPDATE chunk SET doc_embedding = %(doc_embedding)s" \
                           " WHERE sectionid =  %(sectionid)s"
        params = {'sectionid': record[0], 'doc_embedding': embeddings}
        chunk_cursor.execute(update_statement, params)
    chunk_cursor.close()
    conn.close()

except Exception as e:
    print(e)
finally:
    if conn is not None:
        conn.close()
