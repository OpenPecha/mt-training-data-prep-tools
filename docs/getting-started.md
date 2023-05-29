# Getting started

Intro

## 1. Prerequisites

- Python 3.6 or higher
- Pip
- OpenAI API key for text cleanup commands

## 2. Installation

1. Clone the repo `git clone https://github.com/OpenPecha/mt-training-data-prep-tools.git`
2. Install with `pip install -e .`

## 3. Configuration

1. Environment variables

   - `OPENAI_API_KEY` environment variable for cleanup commands
   - `GITHUB_USERNAME`: github username
   - `GITHUB_EMAIL`: github verified email
   - `GITHUB_TOKEN`: github token with read and write access to [MonlamAI](https://github.com/MonlamAI) repos.
   - `MAI_GITHUB_ORG`: MonlamAI github org name
   - `OPENPECHA_DATA_GITHUB_ORG`: openpecha data github org which is `OpenPecha-Data`

## 4. Short how-to

1. add text pair to a collection and create Aligments (TM)

   ```bash
   python -m op_mt_tools.cli.add_texts_pair <collection_path> --text_ids <text_id1> <text_id2>
   ```

   for batch processing

   ```bash
   python -m op_mt_tools.cli.add_texts_pair <collection_path> --text_ids --text_ids $(cat data/text_pairs_list.txt)
   ```

   example `text_pair_list.txt`

   ```

   0504 0702 0709 0710 0723 0725 0726 0728 0746 0747 0751

   ```

2. English text cleanup

   ```bash
   python -m op_mt_tools.cli.en_text_cleanup <collection_path>
   ```

3. Export TMs

   clone this repo https://github.com/MonlamAI/MonlamAI_TMs

   ```bash
   python -m op_mt_tools.tm <path_to_MonlamAI_TMs_repo> --text_id $(cat text_pairs_list.txt)
   ```

   example `text_pair_list.txt`

   ```
   0504 0702 0709 0710 0723 0725 0726 0728 0746 0747 0751
   ```

## 5. Troubleshooting

1. Make sure the `GITHUB_TOKEN` has read and write access to [MonlamAI](https://github.com/MonlamAI) repos.
1. Make sure the `OPENAI_API_KEY` is valid.

Get more help [here](help.md).
