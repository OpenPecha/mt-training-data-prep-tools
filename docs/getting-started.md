# Getting started

## 1. Prerequisites

- Python 3.6 or higher

## 2. Installation

1. Clone the repo `git clone https://github.com/OpenPecha/mt-training-data-prep-tools.git`
2. Install with `pip install -e .`

## 3. Configuration

1. Environment variables

   - `GITHUB_USERNAME`: github username
   - `GITHUB_EMAIL`: github verified email
   - `GITHUB_TOKEN`: github token with read and write access to [MonlamAI](https://github.com/MonlamAI) repos.
   - `MAI_GITHUB_ORG`: MonlamAI github org name which is `MonlamAI`
   - `MAI_TMS_PUBLISH_TODO_REPO`: [MonlamAI_TMs_Publish_TODO](https://github.com/OpenPecha-Data/C1A81F448) repo name
   - `OPENPECHA_DATA_GITHUB_ORG`: openpecha data github org which is `OpenPecha-Data`
   - `HF_TOKEN`: huggingface token to trigger the text aligner to create Translation Memory (TM)
   - `OPENAI_API_KEY`: (_optional_) for cleanup commands for English text

## 4. Short how-to

If you looking for how to run the data pipeline then follow this [link](data-pipeline.md).

### Following are the step by step commands to run the pipeline manually

check out this [wokflow digram](data-pipeline.md#workflow-diagram) to better understand what the following commands does.

1. **Cleanup English text** (_Optional_)

   ```bash
   python -m op_mt_tools.cli.en_text_cleanup <collection_path>
   ```

1. **Add text pair to a collection and triggers the Aligner to create TM**

   Overview:

   - takes list of text_pair ids as input
   - preprocess `EN` and `BO` texts
   - add the preproces text to the collection view
   - Triggers the text aligner to create TM from the preprocess text
     - here is alinger on [huggingface](https://huggingface.co/spaces/openpecha/tibetan-aligner-api)
     - here the [source code](https://github.com/OpenPecha/tibetan-aligner-hf-space)

   clone this collection repo https://github.com/OpenPecha-Data/C1A81F448

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

1. **Export the TMs**

   clone this repo https://github.com/MonlamAI/MonlamAI_TMs

   ```bash
   python -m op_mt_tools.tm <path_to_MonlamAI_TMs_repo> --text_id $(cat text_pairs_list.txt)
   ```

   example `text_pair_list.txt`

   ```
   0504 0702 0709 0710 0723 0725 0726 0728 0746 0747 0751
   ```

1. **Publish new official release of TMs**

   Clone the following repos:

   - https://github.com/MonlamAI/MonlamAI_TMs
   - https://github.com/MonlamAI/MonlamAI_TMs_Publish_TODO

   ```bash
   python -m op_mt_tools.publish <path_to_MonlamAI_TMs_repo> --publish_todo_path <path_to_MonlamAI_TMs_Publish_TODO_repo>
   ```

## 5. Troubleshooting

1. Make sure all the environment variables are set properly.
1. Make sure the `GITHUB_TOKEN` has read and write access to [MonlamAI](https://github.com/MonlamAI) repos.
1. Make sure the `OPENAI_API_KEY` is valid.

Get more help [here](help.md).
