import os
import re
from pathlib import Path
from typing import List

import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo-0301"


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


CLEANUP_PROMPT = """
Perform the following actions:
1 - Split the text delimited by triple backtickcs into sentences.
2 - Join sentences that are split across lines.
3 - Delete page numbers.
4 - Never change the text unless it's a spelling mistake.
5 - Output each sentence on a new line.

Text:
```{}```
"""


def split_document(
    document: str, prompt_template: str, max_tokens: int = 4097
) -> List[str]:
    """Splits a document into chunks of text that are less than max_tokens long."""
    prompt_template_tokens = num_tokens_from_messages(prompt_template.format(""))

    chunks = []
    current_chunk = []
    sentences = re.split("(?<=[.!?]) +", document)
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


def get_completion(prompt, model=OPENAI_MODEL):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_sents_with_chatgpt(text: str) -> List[str]:
    prompt = CLEANUP_PROMPT.format(text)
    response = get_completion(prompt)
    return response.split("\n")


def run_cleanup(fn: Path) -> Path:
    cleaned_fn = fn.parent / f"[GPT_CLEANED]_{fn.stem}.txt"
    text = fn.read_text(encoding="utf-8")
    with cleaned_fn.open("+a") as cleaned_file:
        for chunk in split_document(text, prompt_template=CLEANUP_PROMPT):
            sents = get_sents_with_chatgpt(chunk)
            cleaned_file.writelines(sents)
    return cleaned_fn
