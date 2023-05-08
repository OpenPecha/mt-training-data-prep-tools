import os
from collections.abc import Generator
from pathlib import Path
from typing import List

import openai

CHATGPT_CONTEXT_LENGTH = 1024
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_text_chunks(text: str) -> Generator[str, None, None]:
    start = 0
    end = 0
    while end > len(text):
        end = text.find(
            ".",
            start,
            start + CHATGPT_CONTEXT_LENGTH,
        )
        yield text[start:end]
        start = end + 1


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
        for chunk in get_text_chunks(text):
            sents = get_sents_with_chatgpt(chunk)
            cleaned_file.writelines(sents)
    return cleaned_fn
