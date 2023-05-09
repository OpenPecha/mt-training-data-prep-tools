import os
import re
from collections.abc import Generator
from pathlib import Path
from typing import List

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def split_document(document, max_tokens=4096) -> Generator[str, None, None]:
    sentences = re.split("(?<=[.!?]) +", document)
    chunk = []

    for sentence in sentences:
        chunk.append(sentence)
        # Check if the current chunk has more tokens than the limit
        if len(" ".join(chunk).split()) > max_tokens:
            # If it exceeds the limit, remove the last added sentence and store the chunk
            chunk.pop()
            chunk = [sentence]

        yield " ".join(chunk)
        chunk = []


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_sents_with_chatgpt(text: str) -> List[str]:
    prompt = f"""
Perform the following actions:
1 - Split the text delimited by triple backtickcs into sentences.
2 - Join sentences that are split across lines.
3 - Delete page numbers.
4 - Never change the text unless it's a spelling mistake.
5 - Output each sentence on a new line.

Text:
```{text}```
"""
    response = get_completion(prompt)
    return response.split("\n")


def cleaning_pipeline(fn: Path) -> Path:
    cleaned_fn = fn.parent / f"[GPT_CLEANED]_{fn.stem}.txt"
    text = fn.read_text(encoding="utf-8")
    with cleaned_fn.open("+a") as cleaned_file:
        for chunk in split_document(text):
            sents = get_sents_with_chatgpt(chunk)
            cleaned_file.writelines(sents)
    return cleaned_fn
