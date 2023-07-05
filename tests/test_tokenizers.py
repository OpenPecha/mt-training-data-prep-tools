import pytest

from op_mt_tools.tokenizers import (
    bo_preprocess,
    bo_sent_tokenizer,
    en_preprocess,
    en_sent_tokenizer,
    en_word_tokenizer,
    find_splited_affix,
    fix_splited_affix,
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
        == "༄༅།། ཞོགས་པ་སྔ་པོར་ལངས་པ།། \n༄༅༅།། ན་མོ་གུ་རུ།\nདེའི་རྐྱེན་པས་མཐའ་མར་གྲོགས་པོ་\n"
    )


def test_bo_sent_tokenizer_affix():
    text = "ཨ་རིའི་ས་ཞེས་པས་བཤད་པ་ལྟར་ན།"

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 1


def test_find_splited_affix():
    s = [
        "་དད་པ་འི་",
        "་དད་པེ་འི་",
        "་དད་པོ་འི་",
        "གྱུར་བ་འི་",
        "གྱུར་བེ་འི་",
        "གྱུར་བུ་འི་",
        "གྱུར་བོ་འི་",
    ]
    for i in s:
        assert find_splited_affix(i)


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        ("དད་པ་འི་", "དད་པའི་"),
        ("དད་པེ་འི་", "དད་པེའི་"),
        ("དད་པོ་འི་", "དད་པོའི་"),
        ("གྱུར་བ་འི་", "གྱུར་བའི་"),
        ("གྱུར་བེ་འི་", "གྱུར་བེའི་"),
        ("གྱུར་བུ་འི་", "གྱུར་བུའི་"),
        ("གྱུར་བོ་འི་", "གྱུར་བོའི་"),
    ],
)
def test_remove_preceding_space(input_text, expected_output):
    assert fix_splited_affix(input_text) == expected_output
