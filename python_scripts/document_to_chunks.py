"""
This script is used to load my Word files (docx) using UnstructuredWordDocumentLoader
Then it is split in chunks using RecursiveCharacterTextSplitter and write all the chunks in
a text file.
I will use those text file later to load in the database.
"""
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import NLTKTextSplitter
import re
from unstructured.cleaners.core import (clean_extra_whitespace,
                                        replace_unicode_quotes,
                                        clean_bullets,
                                        group_broken_paragraphs,
                                        clean_dashes,
                                        clean_non_ascii_chars
                                        )
from unstructured.partition.docx import partition_docx
from tqdm.auto import tqdm
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from unstructured.documents.elements import Text


def docx_partition(docx_file):
    raw_docx_element = partition_docx(filename=docx_file,
                                      infer_table_structure=True,
                                      chunking_strategy="by_title",
                                      max_characters=4000,
                                      new_after_n_chars=3800,
                                      combine_text_under_n_chars=2000
                                      )
    docx_tables = []
    docx_texts = []
    for elements in raw_docx_element:
        if "unstructured.documents.elements.Table" in str(type(elements)):
            docx_tables.append(str(elements))
        elif "unstructured.documents.elements.CompositeElement" in str(type(elements)):
            docx_texts.append(str(elements))
    for elements in raw_docx_element:
        print(str(elements))
        print("************")
    return docx_tables, docx_texts


def docx_partition_v2(docx_file):
    raw_docx_element = partition_docx(filename=docx_file,
                                      infer_table_structure=True,
                                      strategy="hi_res",
                                      model_name="yolox",
                                      max_characters=4000,
                                      new_after_n_chars=3800,
                                      combine_text_under_n_chars=2000
                                      )
    docx_tables = []
    docx_texts = []
    # print(raw_docx_element)
    for elements in raw_docx_element:
        docx_texts.append(str(elements))
    for text in docx_texts:
        print(text)
        print("*********")
    return docx_texts


def load_word_doc(word_file):
    loader = UnstructuredWordDocumentLoader(word_file, mode="single",  # 'elements', 'single'
                                            strategy="hi_res",
                                            post_processors=[clean_extra_whitespace,
                                                             replace_unicode_quotes,
                                                             clean_bullets,

                                                             ]
                                            )
    word_file_data = loader.load()
    # print(word_file_data[10])
    return word_file_data


def split_in_chunks_v2(my_document):
    model_name = 'sentence-transformers/msmarco-distilbert-base-v4'
    model = SentenceTransformer(model_name)
    print("Model max sequence length:", model.max_seq_length)
    text_splitter = (
        RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer=AutoTokenizer.from_pretrained(model_name),
            chunk_size=model.max_seq_length - 50,
            chunk_overlap=int((model.max_seq_length - 50) / 5)
        ))
    texts = text_splitter.split_documents(my_document)
    return texts


def split_in_chunks(my_document):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        # separators=['\n\n']
    )
    texts = text_splitter.split_documents(my_document)
    return texts


def split_in_text_chunks(my_document):
    chunks = []
    # meta_data_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    for doc in tqdm(my_document):
        texts = text_splitter.split_text(doc)
        chunks.append(texts)
        # meta_data_chunks.append(doc.meta_data)
    return chunks


def split_in_chunks_nltk(my_document):
    text_splitter = NLTKTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(my_document)
    return texts


if __name__ == '__main__':
    # Load the BPD_Calculate_Price and maintain price.docx
    file_data = load_word_doc(r"C:\Saubhik\Project Automation\hybrid_search"
                              r"\data\Ingestion\R1.0_20.22.12_BPD_Calculate_Price and maintain price.docx")

    text_chunks = split_in_chunks_v2(file_data)

    with open(r"data\text_chunks\price_chunk.txt", 'w', encoding='utf-8') as chunk_file_1:
        for text in text_chunks:
            # chunk_file_1.write(str(' '.join(text)))
            remove_citations = lambda text_c: re.sub("[\[].*?[\]]", "", text_c)
            element = Text(text.page_content)
            element.apply(remove_citations)
            element = clean_dashes(str(element))
            element = clean_extra_whitespace(str(element))
            para_split_re = re.compile(r"(\s*\n\s*){3}")
            element = group_broken_paragraphs(str(element), paragraph_split=para_split_re)
            element = clean_extra_whitespace(str(element))
            element = clean_non_ascii_chars(str(element))
            chunk_file_1.write(str(element))
            chunk_file_1.write("\n\n")

    # Load the BPD_Process_Sales_Ord.docx
    file_data = load_word_doc(r"C:\Saubhik\Project Automation\hybrid_search"
                              r"\data\Ingestion\R1.0_20.17.12_BPD_Process_Sales_Ord.docx")
    text_chunks = split_in_chunks_v2(file_data)
    with open(r"data\text_chunks\sales_order.txt", 'w', encoding='utf-8') as chunk_file_1:
        for text in text_chunks:
            # chunk_file_1.write(str(' '.join(text)))
            remove_citations = lambda text_c: re.sub("[\[].*?[\]]", "", text_c)
            element = Text(text.page_content)
            element.apply(remove_citations)
            element = clean_dashes(str(element))
            element = clean_extra_whitespace(str(element))
            para_split_re = re.compile(r"(\s*\n\s*){3}")
            element = group_broken_paragraphs(str(element), paragraph_split=para_split_re)
            element = clean_extra_whitespace(str(element))
            element = clean_non_ascii_chars(str(element))
            chunk_file_1.write(str(element))
            chunk_file_1.write("\n\n")

    # Load the BPD_Process_Scheduling_Agreement.docx
    file_data = load_word_doc(r"C:\Saubhik\Project Automation\hybrid_search"
                              r"\data\Ingestion\R1.0_20.17.11_BPD_Process_Scheduling_Agreement.docx")
    text_chunks = split_in_chunks_v2(file_data)
    with open(r"data\text_chunks\scheduling_agent.txt", 'w', encoding='utf-8') as chunk_file_1:
        for text in text_chunks:
            # chunk_file_1.write(str(' '.join(text)))
            remove_citations = lambda text_c: re.sub("[\[].*?[\]]", "", text_c)
            element = Text(text.page_content)
            element.apply(remove_citations)
            element = clean_dashes(str(element))
            element = clean_extra_whitespace(str(element))
            para_split_re = re.compile(r"(\s*\n\s*){3}")
            element = group_broken_paragraphs(str(element), paragraph_split=para_split_re)
            element = clean_extra_whitespace(str(element))
            element = clean_non_ascii_chars(str(element))
            chunk_file_1.write(str(element))
            chunk_file_1.write("\n\n")

