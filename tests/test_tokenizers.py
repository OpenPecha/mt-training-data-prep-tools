from op_mt_tools.tokenizers import bo_sent_tokenizer, en_sent_tokenizer


def test_en_sent_tokenizer():
    text = "This is a test. This is another test."
    sents = en_sent_tokenizer(text)

    assert sents == "This is a test.\nThis is another test."


def test_bo_sent_tokenizer():
    text = (
        "༄༅། །རྗེ་བཙུན་མི་ལ་རས་པའི་རྣམ་ཐར་རྒྱས་པར་ཕྱེ་བ་མགུར་འབུམ་ཞེས་བྱ་བ་བཞུགས་སོ། །"
        "༄༅༅། །ན་མོ་གུ་རུ། རྣལ་འབྱོར་གྱི་དབང་ཕྱུག་རྗེ་བཙུན་མི་ལ་རས་པ་དེ་ཉིད། མཆོང་ལུང་ཁྱུང་གི་རྫོ"
    )
    sents = bo_sent_tokenizer(text)

    assert len(sents.splitlines()) == 2
