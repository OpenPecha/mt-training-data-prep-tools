"""
The module is for checking quality of English source text
"""
from typing import Set

from op_mt_tools.tokenizers import en_word_tokenizer

# Types
WORD = str


def calculate_oov_rate(vocabulary: Set[WORD], text):
    """
    Calculate the out-of-vocabulary (OOV) rate of a text given a vocabulary.

    Args:
    vocabulary (set): The set of words in the vocabulary.
    text (list): The text to analyze, tokenized into words.

    Returns:
    float: The OOV rate of the text.
    """
    tokens = en_word_tokenizer(text)
    text_vocab = set(tokens)
    oov_words = text_vocab - vocabulary
    oov_rate = len(oov_words) / len(text_vocab)
    return oov_rate
