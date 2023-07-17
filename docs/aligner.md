# Aligner

## Intro

[Aligner](https://huggingface.co/spaces/openpecha/tibetan-aligner-api) is a service to create Translation Memory (TM) from the text pairs (English and Tibetan). It's using [align-tibetan](https://github.com/sebastian-nehrdich/align-tibetan) under the hood.

Check out aligner section of the data pipeline [workflow diagram](data-pipeline.md#workflow-diagram) to understand what this service does.

## Links

- service: https://huggingface.co/spaces/openpecha/tibetan-aligner-api
- source code:
- service: https://huggingface.co/spaces/openpecha/tibetan-aligner-api

## 1. Prerequisites

- Python 3.6 or higher

## 2. Installation

```bash
git clone https://huggingface.co/spaces/openpecha/tibetan-aligner-api
cd tibetan-aligner-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configuration

1. Environment variables

   - `GITHUB_USERNAME`: github username
   - `GITHUB_EMAIL`: github verified email
   - `GITHUB_TOKEN`: github token with read and write access to [MonlamAI](https://github.com/MonlamAI) repos.
   - `MAI_GITHUB_ORG`: MonlamAI github org name which is `MonlamAI`
   - `MAI_TMS_PUBLISH_TODO_REPO`: [MonlamAI_TMs_Publish_TODO](https://github.com/OpenPecha-Data/C1A81F448) repo name

## Running the aligner

uncomment the input value in `app.py` and run the following command

```bash
gradio app.py
```

## Usage

Currently, we are allowing it be used via API only.

### For Small Text

1. Go to https://huggingface.co/spaces/openpecha/tibetan-aligner-api
1. Click on `Use via API` at the bottom to see how to use it.

### For Large Text

Check out `create_tm` function from [`op_mt_tools.tm`](https://github.com/OpenPecha/mt-training-data-prep-tools/blob/main/src/op_mt_tools/tm.py) module.

## Development

Checkout huggingface space [docs](https://huggingface.co/docs/hub/spaces-overview) and Gradio [docs](https://www.gradio.app/docs/)
for more details.

### Installation

follow the steps from [Installation](#2-installation) section.

### Running the aligner

```bash
gradio app.py
```

### Upgrading the aligner source

1. Clone the aligner source code

   ```bash
   git clone https://github.com/OpenPecha/tibetan-aligner.git
   ```

1. Import the aligner source code

   ```bash
   python import_tibetan_aligner_source.py <path_to_tibetan-aligner>
   ```

### Deploying

After making changes to the source code, run the following command to deploy the aligner.

```bash
git push origin main
```
