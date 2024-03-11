from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import DistanceStrategy


CONNECTION_STRING = "postgresql+psycopg2://saubhik:oracle@localhost:54322/postgrdb"
COLLECTION_NAME = 'chunk'


def semantic_search():
    docs = []
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/msmarco-distilbert-base-v4")
    db = PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        distance_strategy=DistanceStrategy.COSINE,
        embedding_length=768
    )
    # We specify the number of results we want to retrieve (k=5)
    retriever = db.as_retriever(search_type="similarity",
                                search_kwargs={'k': 5}
                                )  # default 4
    return retriever
