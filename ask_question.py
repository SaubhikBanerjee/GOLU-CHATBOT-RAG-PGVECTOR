from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from modules.prompts import qa_template
from modules.llm import llm
from modules.langchain_pgvector import semantic_search
import timeit


# Wrap prompt template in a PromptTemplate object
def set_qa_prompt():
    prompt = PromptTemplate(template=qa_template,
                            input_variables=['context', 'question'])
    return prompt


def build_retrieval_qa(_llm, prompt):
    retriever = semantic_search()
    dbqa = RetrievalQA.from_chain_type(llm=_llm,
                                       chain_type='stuff',
                                       retriever=retriever,
                                       return_source_documents=True,
                                       verbose=True,
                                       chain_type_kwargs={'prompt': prompt})
    return dbqa


if __name__ == '__main__':
    query = input("Please enter the question: ")
    start_time = timeit.default_timer()  # Start timer
    # Starting semantic search.
    qa_prompt = set_qa_prompt()
    dbqa = build_retrieval_qa(llm, qa_prompt)

    response = dbqa({'query': query})
    print(f'\nAnswer: {response["result"]}')
    print('*' * 50)
    source_docs = response['source_documents']
    for i, doc in enumerate(source_docs):
        print(f'\nSource Document {i + 1}\n')
        print(f'Source Text: {doc.page_content}')
        print(f'Document Name: {doc.metadata["source"]}')
        print(f'Page Number: {doc.metadata["page"]}\n')
        print('-' * 50)  # Formatting separator
    print('=' * 50)
    end_time = timeit.default_timer()  # End timer
    print(f"Time to retrieve response (minute(s)): {(end_time - start_time)/60}")
