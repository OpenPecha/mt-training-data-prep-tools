from pathlib import Path

import pytest

from op_mt_tools.cleanup import (
    cleanup_en,
    combine_chunks,
    find_failed_cleanup_chunks,
    split_document,
)


# @pytest.mark.skip(reason="Need to Mock OpenAI API")
def test_split_document():
    fn = Path(__file__).parent / "manual" / "uncleaned_texts" / "01.txt"
    text = fn.read_text()

    sents = split_document(text)

    assert sents == ["Hello World.", "Hello World"]


@pytest.mark.skip(reason="Need to Mock OpenAI API")
def test_run_cleanup():
    fn = Path(__file__).parent / "manual" / "uncleaned_texts" / "01.txt"

    cleaned_fn = cleanup_en(fn)

    assert cleaned_fn.is_file()


@pytest.mark.skip(reason="Need to Mock OpenAI API")
def test_find_failed_cleanup_chunks():
    text_path = Path(__file__).parent / "manual" / "uncleaned_texts"

    failed_chunks = find_failed_cleanup_chunks(text_path)

    assert failed_chunks == [1]


@pytest.mark.skip(reason="need large data")
def test_combine_chunks():
    text_dir = Path(__file__).parent / "manual" / "uncleaned_texts"
    chunks_dir = text_dir / "chunks"
    output_fn = text_dir / "[AUTO_CLEANED]_01.txt"

    combine_chunks(chunks_dir, output_fn)

    assert output_fn.is_file()
