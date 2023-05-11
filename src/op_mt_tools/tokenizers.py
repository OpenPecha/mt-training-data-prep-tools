import re

import botok
import spacy

bo_word_tokenizer = None
nlp = spacy.load("en_core_web_sm")
nlp.max_length = 2000000

SENT_PER_LINE_STR = str  # sentence per line string


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
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return join_sentences(sentences)


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

    # fmt: off
    opening_puncts = ['༁', '༂', '༃', '༄', '༅', '༆', '༇', '༈', '༉', '༊', '༑', '༒', '༺', '༼', '༿', '࿐', '࿑', '࿓', '࿔', '࿙']  # noqa: E501
    closing_puncts = ['།', '༎', '༏', '༐', '༔', '༴', '༻', '༽', '༾', '࿚']  # noqa: E501
    skip_chunk_types = [botok.vars.CharMarkers.CJK.name, botok.vars.CharMarkers.LATIN.name]
    # fmt: on

    # Regex to improve the chunking of shunits, this will be replaced by a better sentence segmentation in botok
    r_replace = [
        (r"༼༼[༠-༩]+[བན]༽", r""),    # delete source image numbers `ས་༼༤བ༽མེད་བ` 
        (r"([^ང])་([༔།])", r"\1\2"),  # delete spurious spaces added by botok in the cleantext values
        (r"([།གཤ]{1,2})\s+(།{1,2})", r"\1\2 "),   # Samdong Rinpoche style double shad. This needs to be applied on inference input
        # (r"", r""),
    ]

    text = bo_preprocess(text)
    sents_text = ""
    tokenizer = get_bo_word_tokenizer()
    tokens = tokenizer.tokenize(text)
    for token in tokens:
        if token.chunk_type in skip_chunk_types:
            continue
        token_text = get_token_text(token)
        if any(punct in token_text for punct in opening_puncts):
            sents_text += token_text.strip()
        elif any(punct in token_text for punct in closing_puncts):
            sents_text += token_text.strip() + "\n"
        else:
            sents_text += token_text

    for fr, to in r_replace:
        sents_text = re.sub(fr, to, sents_text)

    return sents_text


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    if lang == "en":
        # Asuming text is already sentence per line
        return text
    elif lang == "bo":
        return bo_sent_tokenizer(text)
    else:
        raise NotImplementedError
