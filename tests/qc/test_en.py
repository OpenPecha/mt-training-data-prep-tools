from op_mt_tools.qc.en import calculate_oov_rate


def test_calculate_oov_rate():
    text = "This is a xxxx test."
    vocab = {"This", "is", "a", "test"}
    oov_rate = calculate_oov_rate(vocab, text)
    assert oov_rate == 1 / 3
