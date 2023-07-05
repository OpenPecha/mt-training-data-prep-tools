import re
from typing import List, Tuple

import botok
from spacy.lang.en import English

bo_word_tokenizer = None
en_nlp = English()
en_nlp.add_pipe("sentencizer")
en_nlp.max_length = 5000000

# Types
SENT_PER_LINE_STR = str  # sentence per line string
IS_AFFIX_PART = bool
SENTS_WORDS = List[Tuple[str, IS_AFFIX_PART]]


def get_bo_word_tokenizer():
    global bo_word_tokenizer
    if bo_word_tokenizer is None:
        bo_word_tokenizer = botok.WordTokenizer()
    return bo_word_tokenizer


def join_sentences(sentences):
    """Join sentences into a text with one sentence per line."""
    return "\n".join(sentences)


def en_preprocess(text: str) -> str:
    re_sub = [(r"\r\n", " "), (r"\n", " "), (r"\s{2,}", " "), (r"\t", " ")]
    for pattern, repl in re_sub:
        text = re.sub(pattern, repl, text)
    return text


def en_sent_tokenizer(text: SENT_PER_LINE_STR) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    text = en_preprocess(text)
    doc = en_nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return join_sentences(sentences)


def en_word_tokenizer(text: str) -> List[str]:
    """Tokenize a text into words."""
    doc = en_nlp(text)
    words = [token.text for token in doc]
    return words


def bo_preprocess(text: str) -> str:
    text = text.replace("\r", "").replace("\n", "")
    return text


def bo_sent_tokenizer(text: str) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""

    def get_token_text(token):
        if hasattr(token, "text_cleaned") and token.text_cleaned:
            return token.text_cleaned
        else:
            return token.text

    def is_affix_part(token):
        affix_parts = ["ར་", "ས་", "འི་"]
        text = get_token_text(token)
        if text in affix_parts and token.pos == "PART":
            return True
        else:
            return False

    def merge_affix_part(sents_words: SENTS_WORDS) -> List[str]:
        merged_affix_words: List[str] = []
        for i in range(len(sents_words)):
            word, is_affix_part = sents_words[i]
            if is_affix_part:
                prev_word, _ = sents_words[i - 1]
                if prev_word[-1] == "་":
                    prev_word = prev_word[:-1]
                merged_affix_words[-1] = (
                    prev_word + word
                )  # remove last tsek of prev_word and add punct(word)
            else:
                merged_affix_words.append(word)
        return merged_affix_words

    # fmt: off
    opening_puncts = ['༁', '༂', '༃', '༄', '༅', '༆', '༇', '༈', '༉', '༊', '༑', '༒', '༺', '༼', '༿', '࿐', '࿑', '࿓', '࿔', '࿙']  # noqa: E501
    closing_puncts = ['།', '༎', '༏', '༐', '༔', '༴', '༻', '༽', '༾', '࿚']  # noqa: E501
    skip_chunk_types = [botok.vars.CharMarkers.CJK.name, botok.vars.CharMarkers.LATIN.name]
    # fmt: on

    # Regex to improve the chunking of shunits, this will be replaced by a better sentence segmentation in botok
    r_replace = [
        (r"༼༼[༠-༩]+[བན]༽", r""),  # delete source image numbers `ས་༼༤བ༽མེད་བ`
        (
            r"([^ང])་([༔།])",
            r"\1\2",
        ),  # delete spurious spaces added by botok in the cleantext values
        (
            r"([།གཤ]{1,2})\s+(།{1,2})",
            r"\1\2 ",
        ),  # Samdong Rinpoche style double shad. This needs to be applied on inference input
        # (r"", r""),
    ]

    text = bo_preprocess(text)
    sents_words: SENTS_WORDS = []
    tokenizer = get_bo_word_tokenizer()
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        if token.chunk_type in skip_chunk_types:
            continue
        token_text = get_token_text(token)
        if any(punct in token_text for punct in opening_puncts):
            sents_words.append((token_text.strip(), False))
        elif any(punct in token_text for punct in closing_puncts):
            sents_words.append((token_text.strip(), False))
            sents_words.append(("\n", False))
        else:
            sents_words.append((token_text, is_affix_part(token)))

    sents_text = "".join(merge_affix_part(sents_words))

    for fr, to in r_replace:
        sents_text = re.sub(fr, to, sents_text)

    return sents_text


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    if lang == "en":
        return en_sent_tokenizer(text)
    elif lang == "bo":
        return bo_sent_tokenizer(text)
    else:
        raise NotImplementedError
