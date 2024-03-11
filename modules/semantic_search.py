import psycopg2 as pg
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from modules.read_config import ReadConfig


def vector_search(query_string):
    my_config = ReadConfig("config/config.ini")
    model = SentenceTransformer(my_config.SentenceTransformer_model)
    conn = None
    try:

        # Connecting to PostgreSQL cluster.
        conn = pg.connect(
            host=my_config.db_server_address,
            database=my_config.db_database_name,
            user=my_config.db_user_name,
            password=my_config.db_password,
            port=my_config.db_port
        )
        conn.autocommit = True

        # Creating a Cursor
        imdb_review_cursor = conn.cursor()
        imdb_review_cursor.execute("SET search_path="+my_config.db_connecting_schema)
        # Registering vector is necessary.
        register_vector(conn)
        # Check the connectivity and check the database version.
        imdb_review_cursor.execute("SELECT version()")
        db_version = imdb_review_cursor.fetchone()
        print("Connected to: ", db_version)
        # Now getting the query embeddings for the query text.
        query_text = query_string
        query_embeddings = model.encode(query_text)
        sql_text = "SELECT sectionid, sectiontext FROM "+my_config.query_table_name+" " \
                   "WHERE 1=1  " \
                   " and doc_embedding_msmacro IS NOT NULL" \
                   " ORDER BY 1- (doc_embedding_msmacro <=> %(query_embeddings)s) DESC" \
                   " LIMIT "+my_config.limit_rows
        params = {'query_embeddings': query_embeddings}
        imdb_review_cursor.execute(sql_text, params)
        sql_result = imdb_review_cursor.fetchall()
        imdb_review_cursor.close()
        conn.close()
        return sql_result

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def vector_search_v2(query_string):
    my_config = ReadConfig("config/config.ini")
    model = SentenceTransformer(my_config.SentenceTransformer_model)
    conn = None
    try:

        # Connecting to PostgreSQL cluster.
        conn = pg.connect(
            host=my_config.db_server_address,
            database=my_config.db_database_name,
            user=my_config.db_user_name,
            password=my_config.db_password,
            port=my_config.db_port
        )
        conn.autocommit = True

        # Creating a Cursor
        imdb_review_cursor = conn.cursor()
        imdb_review_cursor.execute("SET search_path="+my_config.db_connecting_schema)
        # Registering vector is necessary.
        register_vector(conn)
        # Check the connectivity and check the database version.
        imdb_review_cursor.execute("SELECT version()")
        db_version = imdb_review_cursor.fetchone()
        print("Connected to: ", db_version)
        # Now getting the query embeddings for the query text.
        query_text = query_string
        query_embeddings = model.encode(query_text)
        sql_text = "SELECT sectionid, coalesce(table_section, sectiontext) FROM "+my_config.query_table_name+" " \
                   "WHERE 1=1  " \
                   " and doc_embedding_msmacro IS NOT NULL" \
                   " ORDER BY 1- (doc_embedding_msmacro <=> %(query_embeddings)s) DESC" \
                   " LIMIT "+my_config.limit_rows
        params = {'query_embeddings': query_embeddings}
        imdb_review_cursor.execute(sql_text, params)
        sql_result = imdb_review_cursor.fetchall()
        imdb_review_cursor.close()
        conn.close()
        return sql_result

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    sql_results = vector_search("What surcharges is available")
    for record in sql_results:
        print("\033[38;5;208mSection Id: \033[0;0m", record[0])
        print("\033[38;5;208mSection Text: \033[0;0m", record[1])
