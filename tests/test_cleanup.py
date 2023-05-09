from pathlib import Path

import pytest

from op_mt_tools.cleanup import CLEANUP_PROMPT, run_cleanup, split_document


def test_get_text_chunks():
    text = "Hello World. Hello World"

    sents = split_document(text, prompt_template=CLEANUP_PROMPT, max_tokens=75)

    assert sents == ["Hello World.", "Hello World"]


@pytest.mark.skip(reason="Need to Mock OpenAI API")
def test_run_cleanup():
    fn = Path(__file__).parent / "manual" / "uncleaned_texts" / "01.txt"

    cleaned_fn = run_cleanup(fn)

    assert cleaned_fn.is_file()
