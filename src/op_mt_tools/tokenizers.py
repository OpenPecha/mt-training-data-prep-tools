import botok
import spacy

bo_word_tokenizer = botok.WordTokenizer()
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

    text = bo_preprocess(text)
    sents_text = ""
    tokens = bo_word_tokenizer.tokenize(text)
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

    return sents_text


def sent_tokenize(text, lang) -> SENT_PER_LINE_STR:
    """Tokenize a text into sentences."""
    if lang == "en":
        return en_sent_tokenizer(text)
    elif lang == "bo":
        return bo_sent_tokenizer(text)
    else:
        raise NotImplementedError
