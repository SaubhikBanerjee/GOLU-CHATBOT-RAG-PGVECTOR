from nltk.tokenize import MWETokenizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def keywords(question):
    # This list should be dynamically created from a file and new words to be added
    # as and when required.
    extra_stopwords = ["What", "kind", "?", "Where", "can", "to"]
    protected_keywords = ["Scheduling Agreement types"
                          , "ZCSA_CUTREF_CON"
                          , "Sales order types"
                          , "order types"
                          , "Reason for rejection"
                          , "available surcharges"
                          , "condition records available for surcharges"
                          , "pricing conditions"
                          , "Pricing condition master data"
                          , "pricing procedures"
                          , "Pricing for Sales Bill of Material"
                          , "Discount condition types"
                          , "Transaction code for Mass Maintenance of Condition Records"
                          , " transaction code for Scheduling Agreement Upload "
                          , "Transaction code for sales order monitor"
                          , "different PO types used"
                          , "COM Code in the sales order"
                          ]
    protected_tuples = [word_tokenize(word) for word in protected_keywords]
    protected_tuples_underscore = ['_'.join(word) for word in protected_tuples]
    tokenizer = MWETokenizer(protected_tuples)
    # Tokenize the text.
    tokenized_text = tokenizer.tokenize(word_tokenize(question))
    # Replace the underscored protected words with the original MWE
    for i, token in enumerate(tokenized_text):
        if token in protected_tuples_underscore:
            tokenized_text[i] = protected_keywords[protected_tuples_underscore.index(token)]
    english_stopwords = stopwords.words('english')
    english_stopwords.extend(extra_stopwords)
    tokens_wo_stopwords = [t for t in tokenized_text if t not in english_stopwords]
    return tokens_wo_stopwords


if __name__ == '__main__':
    print(keywords("What kind of Scheduling Agreement types are there?"))
    print(' '.join(keywords("What kind of Scheduling Agreement types are there?")))
