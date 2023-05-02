import re

import spacy

nlp = spacy.load("en_core_web_sm")
nlp.max_length = 2000000

SENT_PER_LINE_STR = str  # sentence per line string


def join_sentences(sentences):
    """Join sentences into a text with one sentence per line."""
    return "\n".join(sentences)


def en_preprocess(text: str) -> str:
    text = text.replace("\r", "").replace("\n", "")
    return text


def en_sent_tokenizer(text: str) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""

    text = en_preprocess(text)
    doc = nlp(text)
    sents = [str(s) for s in doc.sents]
    return join_sentences(sents)


def bo_preprocess(text: str) -> str:
    text = text.replace("\r", "").replace("\n", "")
    return text


def bo_sent_tokenizer(text: str) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""

    r_subs = [
        (r"\s{2,}", ""),
        ("^ ", ""),
        (r"\n+", r"\n"),
        ("༌", "་"),
        ("་ ", "་"),
        ("་ ", "་"),
        (r"^་+", ""),
        (r"^་+", ""),
        (r"༌{2,}", "་"),
        (r"་{2,}", "༌"),
        ("།", "།"),
        ("། ། ། །", "།། །།"),
        ("། ། ", "། །"),
        (r"([ག།ཤ] །?)([^\n།])", r"\g<1>\n\g<2>"),
        ("། ", "།"),
    ]

    text = bo_preprocess(text)
    text = re.sub(r"\t", "", text)

    # split on space
    r_split = r"(?<!།\s)\s+(?!\s*།)"
    text = "\n".join([sent for sent in re.split(r_split, text) if sent])

    for f, to in r_subs:
        text = re.sub(f, to, text)

    return text


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    if lang == "en":
        return en_sent_tokenizer(text)
    elif lang == "bo":
        return bo_sent_tokenizer(text)
    else:
        raise NotImplementedError
