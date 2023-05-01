import botok
import spacy

nlp = spacy.load("en_core_web_sm")
bo_work_tokenizer = botok.WordTokenizer()

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

    def _to_string(tokens):
        return "".join(t["text"] for t in tokens)

    text = bo_preprocess(text)
    tokens = bo_work_tokenizer.tokenize(text)
    sents = [_to_string(sent["tokens"]) for sent in botok.sentence_tokenizer(tokens)]
    return join_sentences(sents)


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    if lang == "en":
        return en_sent_tokenizer(text)
    elif lang == "bo":
        return bo_sent_tokenizer(text)
    else:
        raise NotImplementedError
