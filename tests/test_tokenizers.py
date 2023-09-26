from op_mt_tools.tokenizers import (
    bo_preprocess,
    bo_sent_tokenizer,
    en_preprocess,
    en_sent_tokenizer,
    en_word_tokenizer,
)


def test_en_word_tokenizer():
    text = "This is a test."
    tokens = en_word_tokenizer(text)
    assert tokens == ["This", "is", "a", "test", "."]


def test_en_preprocess():
    text = "This is \r\na test.\nThis is another test."
    assert en_preprocess(text) == "This is a test. This is another test."


def test_en_sent_tokenizer():
    text = "This is a test.\nThis is another test."
    sents = en_sent_tokenizer(text)

    assert sents == "This is a test.\nThis is another test."


def test_en_sent_tokenizer_check_output():
    text = ""
    sents = en_sent_tokenizer(text)

    print("\n-----------------------")
    print(sents)


def test_bo_preprocess():
    text = "ཀཀཀ\nཀཀཀ\r\nཀཀཀ\n"
    assert bo_preprocess(text) == "ཀཀཀཀཀཀཀཀཀ"


def test_bo_sent_tokenizer_2():
    text = """
    TibetanBuddhistResourceCenterTextScan Input
    ༄༅། །ཞོགས་པ་སྔ་པོར་ལངས་པ། །
    EMILY༄༅༅། །ན་མོ་གུ་རུ། དེའི་(“”)རྐྱེན་པས་མཐའ་མར་གྲོགས་པོ་
    """

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 3
    assert (
        sents
        == "༄༅།། ཞོགས་པ་སྔ་པོར་ལངས་པ།། \n༄༅༅།། ན་མོ་གུ་རུ།\nདེའི་རྐྱེན་པས་མཐའ་མར་གྲོགས་པོ་"
    )


def test_bo_sent_tokenizer_affix():
    text = "ཞེས་པས་"

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 1
    assert sents == "ཞེས་པས་"


def test_bo_sent_tokenizer_affix_2():
    text = "བཞིན་པའི་"

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 1
    assert sents == "བཞིན་པའི་"


def test_bo_sent_tokenizer_affix_3():
    text = "གསུམ་པའི་པའི་"

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 1
    assert sents == "གསུམ་པའི་པའི་"
