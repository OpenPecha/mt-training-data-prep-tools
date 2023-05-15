from op_mt_tools.tokenizers import (
    bo_preprocess,
    bo_sent_tokenizer,
    en_preprocess,
    en_sent_tokenizer,
)


def test_en_preprocess():
    text = "This is \r\na test.\nThis is another test."
    assert en_preprocess(text) == "This is a test. This is another test."


def test_en_sent_tokenizer():
    text = "This is a test.\nThis is another test."
    sents = en_sent_tokenizer(text)

    assert sents == "This is a test.\nThis is another test."


def test_bo_preprocess():
    text = "ཀཀཀ\nཀཀཀ\r\nཀཀཀ\n"
    assert bo_preprocess(text) == "ཀཀཀཀཀཀཀཀཀ"


def test_bo_sent_tokenizer_2():
    text = """
    TibetanBuddhistResourceCenterTextScan Input
    ༄༅། །རྗེ་བཙུན་མི་ལ་རས་པའི་རྣམ་ཐར་རྒྱས་པར་ཕྱེ་བ་མགུར་འབུམ་ཞེས་བྱ་བ་བཞུགས་སོ། །
    EMILY༄༅༅། །ན་མོ་གུ་རུ། རྣལ་འབྱོར་གྱི་དབང་ཕྱུག་རྗེ་(“”)བཙུན་མི་ལ་རས་པ་དེ་ཉིད།
    """

    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 3
