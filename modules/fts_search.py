import psycopg2 as pg
from pgvector.psycopg2 import register_vector
from modules.read_config import ReadConfig


def phraseto_tsquery(query_text):
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

        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " phraseto_tsquery('english',%(query_string)s)) rnk" \
                   " from chunk " \
                   " where chunk_fts_doc" \
                   " @@ phraseto_tsquery('english',%(query_string)s)" \
                   " ) x    order by  rnk desc limit 2"
        params = {'query_string': query_text}
        imdb_review_cursor.execute(sql_text, params)
        sql_result = imdb_review_cursor.fetchall()
        conn.close()
        return sql_result
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def plainto_tsquery(query_text):
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

        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " plainto_tsquery('english',%(query_string)s)) rnk" \
                   " from chunk " \
                   " where chunk_fts_doc" \
                   " @@ plainto_tsquery('english',%(query_string)s)" \
                   " ) x    order by  rnk desc limit 2"
        params = {'query_string': query_text}
        imdb_review_cursor.execute(sql_text, params)
        sql_result = imdb_review_cursor.fetchall()
        conn.close()
        return sql_result
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


def phraseto_tsquery_v2(query_text, configuration):
    conn = None
    my_config = ReadConfig("config/config.ini")

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
        review_cursor = conn.cursor()
        # The connecting schema, where the table resides
        review_cursor.execute("SET search_path="+my_config.db_connecting_schema)
        # Registering vector is necessary.
        # This is required only if you are using PGVector
        register_vector(conn)

        # Now building the query text. First I use phraseto_tsquery
        # You can play with the query and user a threshold
        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " phraseto_tsquery(%(configuration)s,%(query_string)s)) rnk" \
                   " from "+my_config.query_table_name+" " \
                   " where chunk_fts_doc" \
                   " @@ phraseto_tsquery(%(configuration)s,%(query_string)s)" \
                   " ) x    order by  rnk desc limit "+my_config.limit_rows
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
    my_config = ReadConfig("config/config.ini")

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
        review_cursor = conn.cursor()
        # The connecting schema, where the table resides
        review_cursor.execute("SET search_path="+my_config.db_connecting_schema)

        # Registering vector is necessary.
        # This is required only if you are using PGVector
        register_vector(conn)

        # Now building the query text. Now I use plainto_tsquery
        # You can play with the query and user a threshold
        sql_text = "select * from (" \
                   " select sectionid,sectiontext," \
                   " ts_rank(chunk_fts_doc," \
                   " plainto_tsquery(%(configuration)s,%(query_string)s)) rnk" \
                   " from "+my_config.query_table_name+" " \
                   " where chunk_fts_doc" \
                   " @@ plainto_tsquery(%(configuration)s,%(query_string)s)" \
                   " ) x    order by  rnk desc limit "+my_config.limit_rows
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


if __name__ == '__main__':
    query_string = input("Enter query:")
    sql_results1 = phraseto_tsquery(query_string)
    sql_results2 = plainto_tsquery(query_string)

    # most important records by intersection
    imp_records = list(set(sql_results1) & set(sql_results2))
    for record in imp_records:
        print("\033[92mSection Id: \033[0;0m", record[0])
        print("\033[92mSection Text: \033[0;0m", record[1])

    for record in sql_results1:
        print("\033[38;5;208mSection Id: \033[0;0m", record[0])
        print("\033[38;5;208mSection Text: \033[0;0m", record[1])

    for record in sql_results2:
        print("\033[38;5;208mSection Id: \033[0;0m", record[0])
        print("\033[38;5;208mSection Text: \033[0;0m", record[1])
