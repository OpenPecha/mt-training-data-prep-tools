import os
import re
from pathlib import Path
from typing import List

import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo-0301"
CONTEXT_LENGTH = 4096


def num_tokens_from_messages(text, model=OPENAI_MODEL):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if model == "gpt-3.5-turbo":
        print(
            "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return num_tokens_from_messages(text, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print(
            "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return num_tokens_from_messages(text, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
    elif model == "gpt-4-0314":
        tokens_per_message = 3
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. \
                See https://github.com/openai/openai-python/blob/main/chatml.md \
                for information on how messages are converted to tokens."""
        )
    return len(encoding.encode(text)) + tokens_per_message


# CLEANUP_PROMPT = """
# Your task is to clean up the text delimited by triple backticks.

# Here the criteria for cleaning up the text:
# - Split the text into sentences.
# - Combine chunks that are split across lines to form a sentence.
# - Delete page numbers.
# - Correct spelling mistakes.
# - Delete any text that is not part of the story.

# Never change the text unless it's a spelling mistake.
# Required complete output.

# Format


# Text:
# ```{}```
# """

CLEANUP_PROMPT = """
Use text delimited by <>. \
Split all sentences and format them as a bullet point list. \
Join sentences that are split across lines. \
Delete page numbers but don't change the text.

<{}>
"""


def split_document(document: str, prompt_template: str) -> List[str]:
    """Splits a document into chunks of text that are less than max_tokens long."""
    prompt_template_tokens = num_tokens_from_messages(prompt_template.format(""))
    max_tokens = (
        CONTEXT_LENGTH // 2 - prompt_template_tokens
    )  # https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them#h_051eb08805  # noqa: E501

    chunks = []
    current_chunk = []
    sentences = re.split("(?<=[.!?])", document)
    for sentence in sentences:
        current_chunk.append(sentence)
        # Check if the current chunk has more tokens than the limit
        tokens = num_tokens_from_messages(" ".join(current_chunk))
        if tokens + prompt_template_tokens > max_tokens:
            # If it exceeds the limit, remove the last added sentence and store the chunk
            current_chunk.pop()
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def get_completion(prompt: str, model=OPENAI_MODEL) -> str:
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_sents_with_chatgpt(text: str) -> List[str]:
    def parser_response(response: str) -> List[str]:
        return response.split("- ")

    prompt = CLEANUP_PROMPT.format(text).strip()
    response = get_completion(prompt)
    sents = parser_response(response)
    return sents


def cleanup_en(
    fn: Path, cleaned_file_prefix: str = "[AUTO_CLEANED]", verbose: bool = False
) -> Path:
    """Clean up english text using GPT-3."""
    cleaned_fn = fn.parent / f"{cleaned_file_prefix}_{fn.stem}.txt"
    if cleaned_fn.is_file():
        cleaned_fn.unlink()
    text = fn.read_text(encoding="utf-8")
    with cleaned_fn.open("+a") as cleaned_file:
        doc_chunks = split_document(text, prompt_template=CLEANUP_PROMPT)
        for i, chunk in enumerate(doc_chunks):
            print(f"\t- cleaning chunk {i+1}/{len(doc_chunks)} ...")
            sents = get_sents_with_chatgpt(chunk)
            cleaned_file.writelines(sents)
            if verbose:
                chunks_dir = fn.parent / "chunks"
                chunks_dir.mkdir(exist_ok=True)
                chunk_input_fn = chunks_dir / f"{i:04}_chunk_input.txt"
                chunk_cleaned_fn = chunks_dir / f"{i:04}_chunk_cleaned.txt"
                chunk_input_fn.write_text(chunk, encoding="utf-8")
                chunk_cleaned_fn.write_text("\n".join(sents), encoding="utf-8")
    return cleaned_fn
