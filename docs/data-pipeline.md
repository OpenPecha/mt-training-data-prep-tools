# Data Pipeline

## Overview workflow

## Create New TM

1. Get text list from Ready sheet of [Translation Catalog](https://docs.google.com/spreadsheets/d/14CA5kyoAkty2sHhkMT5ZX05Otm7eSGYAt0zAt59xQwI/edit#gid=1563391012)
1. Go to https://github.com/OpenPecha-Data/C1A81F448
1. Set text list as input (shown in the image below)
   <img width="1255" alt="run_aligner_input" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/9fea13e8-1c83-446f-a96d-cd92fbbaf9f9">
1. Run Alinger (shown in the image below)
   <img width="1762" alt="Run Aligner" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/b5a1170c-8229-487b-9c90-62447fac7038">
1. Check log if the aligner running properly (shown in the image below)
   <img width="1467" alt="Screenshot 2023-05-29 at 4 24 05 PM" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/e46df67e-3f2f-4084-a7fa-8de8701474d7">

## Export TMs

1. clone this repo https://github.com/MonlamAI/MonlamAI_TMs
2. Store all TMs ids in a file `text_pairs_list.txt`. (shown in the example below)

(content of `text_pairs_list.txt`)

```txt
0504 0702 0709 0710 0723 0725 0726 0728 0746 0747 0751
```

3. Run the follwing command to export

```bash
python -m op_mt_tools.tm <path_to_MonlamAI_TMs_repo> --text_id $(cat text_pairs_list.txt)
```

[MonlamAI_TMs](https://github.com/MonlamAI/MonlamAI_TMs) will contain all the exported TMs. Checkout it's README.md for how to use it.

## Publishing TMs as training data

- we have setup corn job to publish new release of training data weekly.
- [Releases](https://github.com/MonlamAI/MonlamAI_TMs/releases) are just github release with date as a version tag.
- We have github [issue](https://github.com/MonlamAI/MonlamAI_TMs/issues) for getting feedback on the each release.

Under the hood it's using `op_mt_tools.publish` to create new release.
