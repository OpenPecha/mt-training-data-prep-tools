from op_mt_tools.cleanup import split_document


def test_get_text_chunks():
    text = "12. 3456. 7890"

    chunks = list(split_document(text, max_tokens=3))

    assert chunks == ["12.", "3456.", "7890"]
