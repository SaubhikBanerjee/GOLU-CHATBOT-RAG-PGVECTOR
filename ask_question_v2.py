from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from modules import qa_template
from modules import llm
import timeit
from modules import vector_search_v2
from langchain_community.retrievers import TFIDFRetriever


# Wrap prompt template in a PromptTemplate object
def set_qa_prompt():
    prompt = PromptTemplate(template=qa_template,
                            input_variables=['context', 'question'])
    return prompt


def build_retrieval_qa(_llm, prompt, _retriever):
    db_qa = RetrievalQA.from_chain_type(llm=_llm,
                                        chain_type='stuff',
                                        retriever=_retriever,
                                        return_source_documents=True,
                                        verbose=True,
                                        chain_type_kwargs={'prompt': prompt})
    return db_qa


if __name__ == '__main__':
    query = input("Please enter the question: ")
    start_time = timeit.default_timer()  # Start timer
    # Starting semantic search.
    result_set = vector_search_v2(query)
    # Getting the retrieved results in a list
    documents = [record[1] for record in result_set]
    retriever = TFIDFRetriever.from_texts(documents)
    qa_prompt = set_qa_prompt()
    dbqa = build_retrieval_qa(llm, qa_prompt, retriever)

    response = dbqa({'query': query})
    # Displaying the outcome.
    print(f'\n\033[92m Answer: \033[0;0m {response["result"]}')
    print("\033[38;5;208m*******************************\033[0;0m")
    source_docs = response['source_documents']
    for i, doc in enumerate(source_docs):
        print(f'\nSource Document {i + 1}\n')
        print(f'Source Text: {doc.page_content}')
        print("\033[38;5;208m*******************************\033[0;0m")
    print('=' * 50)
    end_time = timeit.default_timer()  # End timer
    total_time = (end_time - start_time) / 60
    print("Time to retrieve response %.2f(minute(s)):" % total_time)
