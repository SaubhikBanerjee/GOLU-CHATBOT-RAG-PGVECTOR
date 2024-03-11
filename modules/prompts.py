# Good reads : https://arxiv.org/pdf/2312.16171.pdf
#            : https://medium.com/the-modern-scientist/best-prompt-techniques-for-best-llm-responses-24d2ff4f6bca
#            : https://towardsdatascience.com/how-i-won-singapores-gpt-4-prompt-engineering-competition-34c195a93d41


qa_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

# Defining the template to generate summary
table_summary_template = """
   Write a concise summary of the table, return your responses with 25 lines that cover the key points of the table.
    ```{text}```
    SUMMARY:
    """
table_summary_prompt_text = """You are an assistant tasked with summarizing tables. \
Give a concise summary of the table. Table: {element} """