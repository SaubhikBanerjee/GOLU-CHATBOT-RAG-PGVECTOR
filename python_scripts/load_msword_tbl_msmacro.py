import pandas as pd
from docx import Document
from docx.text.paragraph import Paragraph
import io
import psycopg2 as pg
import uuid
from langchain_community.llms import CTransformers
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document as langDocument
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


def doc_tokenizer():
    model = SentenceTransformer('sentence-transformers/msmarco-distilbert-base-v4')
    print("Model max sequence length:", model.max_seq_length)


def split_in_text_chunks(my_table):
    chunks = []
    # meta_data_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    for my_doc in my_table:
        # texts = text_splitter.split_text(my_doc)
        texts = text_splitter.split_documents(my_doc)
        chunks.append(texts)
        # meta_data_chunks.append(doc.meta_data)
    return chunks


def generate_summary_v2(my_document):
    llm = CTransformers(model=r"C:\Saubhik\Project Automation\hybrid_search\lama2\llama-2-7b-chat.Q8_0.gguf",
                        model_type='llama',  # Model type Llama
                        config={'max_new_tokens': 2048,
                                'temperature': 0.001,
                                'context_length': 4096})
    table_summary_template = """
       Write a detail summary of the table, return your responses that cover the every points of the table. \
       You must explain all the Condition type available with description and business description side by side\
       Think step by step. I’m going to tip $999 for a better solution!
        ```{text}```
        SUMMARY:
        """
    prompt = PromptTemplate.from_template(table_summary_template)
    # Define LLM chain
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain,
                                      document_variable_name="text"
                                      )
    return stuff_chain.invoke(my_document)


def generate_summary_v1(my_document):
    llm = CTransformers(model=r"C:\Saubhik\Project Automation\hybrid_search\lama2\llama-2-7b-chat.Q8_0.gguf",
                        model_type='llama',  # Model type Llama
                        config={'max_new_tokens': 1024,
                                'temperature': 0.001,
                                'context_length': 4096})
    chain = load_summarize_chain(llm, chain_type="stuff"
                                 )
    return chain.run(my_document)


def inert_data(section_text, table_text):
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
    sectionid = str(uuid.uuid4())
    insert_statement = "INSERT INTO chunk (sectionid, sectiontext, table_section) VALUES" \
                       " (%(sectionid)s, %(sectiontext)s, , %(table_section)s)"
    params = {'sectionid': sectionid, 'sectiontext': section_text, 'table_section': table_text}
    chunk_cursor.execute(insert_statement, params)
    chunk_cursor.close()
    conn.close()


def iter_block_items(parent):
    # https://github.com/python-openxml/python-docx/issues/40
    from docx.document import Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import _Cell, Table
    from docx.text.paragraph import Paragraph
    """
    Yield each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph. *parent*
    would most commonly be a reference to a main Document object, but
    also works for a _Cell object, which itself can contain paragraphs and tables.
    """
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    # print('parent_elm: '+str(type(parent_elm)))
    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)  # No recursion, return tables as tables
        # table = Table(child, parent)  # Use recursion to return tables as paragraphs
        # for row in table.rows:
        #     for cell in row.cells:
        #         yield from iter_block_items(cell)


def read_tables_with_head(document):
    para_head = ''
    for iter_block_item in iter_block_items(document):  # Iterate over paragraphs and tables
        # print('iter_block_item type: '+str(type(iter_block_item)))
        if isinstance(iter_block_item, Paragraph):
            paragraph = iter_block_item  # Do some logic here
            if paragraph.style.name.startswith('Heading'):
                para_head = paragraph.text
                # print(paragraph.text)
        else:
            table = iter_block_item
            # print(table)
            data = [[cell.text for cell in row.cells] for row in table.rows]
            df = pd.DataFrame(data)
            df = df.rename(columns=df.iloc[0]).drop(df.index[0]).reset_index(drop=True)
            if not df.empty:
                # df[para_head] = para_head
                if len(para_head) > 1:
                    df.insert(0, para_head, para_head)
                    # print(df.shape[0])
                    md_buf = io.StringIO()
                    df.to_markdown(md_buf, disable_numparse=True)
                    md_buf.seek(0)
                    md_str = md_buf.getvalue()
                    if para_head.strip() in "Price Conditions":
                        md_doc = langDocument(page_content=md_str,
                                              metadata={"source": "user"})
                        # table_summary = generate_summary_v1([md_doc])
                        table_summary = generate_summary_v2([md_doc])
                        print(table_summary)
                        # print("*" * 40)
                        # inert_data(str(table_summary), str(md_str))


if __name__ == '__main__':
    doc = Document(
        "C:\\Saubhik\\Project Automation\\hybrid_search\\data\\Ingestion"
        "\\R1.0_20.22.12_BPD_Calculate_Price and maintain price.docx")
    read_tables_with_head(doc)

