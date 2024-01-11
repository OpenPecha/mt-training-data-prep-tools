# Data Pipeline

## Workflow Diagram

![MonlamAI TM Data Pipeline Workflow](https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/fb8ab76e-08ef-4124-a36f-37e3cb544a94)

## Installation

1. Login into the server via `ssh tenzin@openpecha.bdrc.io`
1. cd into the `~/TM` directory
1. Run `./scripts/install.sh`

## Starting the pipeline

1. Get text list from Ready sheet of [Translation Catalog](https://docs.google.com/spreadsheets/d/14CA5kyoAkty2sHhkMT5ZX05Otm7eSGYAt0zAt59xQwI/edit#gid=1563391012). Here, the text list is list of text ids without the language prefix (like `EN` and `BO`), e.g, text id of `EN0001` and `BO0001` is `0001`
1. Login into the server via `ssh tenzin@openpecha.bdrc.io`
1. cd into the `~/TM` directory 
1. Save the text text pair list in any text file in `./input`, eg: `./input/tm_todo.txt` with a text list like:
   ```
   0001 0002 0003
   ```
1. Now run `./scripts/create_tm.sh input/tm_todo.txt`
1. Check out `stdout` and `stderr` with `tail -f ./nohup.out`

**Note**:

1. To re-run the text id, delete the text id from `~/TM/C1A81F448/C1A81F448.opc/meta.yml` manually. This is because the pipeline will skip the text id if it's already in the `meta.yml` file.

## Publishing a TMs as training dataset

Currently, we are publishing all TM at [dharmamitra](https://github.com/dharmamitra) like this [mitra-mt-en-bo-3](https://github.com/dharmamitra/mitra-mt-en-bo-3)

### Versioning

- Last digit is in the dataset name is the version number. Eg: mitra-mt-en-bo-3, 3 is the version number.
- so the next version will be incremented by 1, eg: mitra-mt-en-bo-4

### Publishing a new version

1. Rename the previous mitra-mt-en-bo repo located in ~/MonlamAI/data/  eg: mitra-mt-en-bo-3 to mitra-mt-en-bo-4
1. Create a github repo with same name as the new version, eg: mitra-mt-en-bo-4 in [dharmamitra github organisation](https://github.com/dharmamitra]
1. Set remote to the new version repo, eg `git remote set-url https://github.com/dharmamitra/mitra-mt-en-bo-4.git`
1. Push the local repo to github
1. Update the readme according to new verison
   1. Title of the version
   1. Download command
   1. Catalog link
1. cd into the `~/TM` directory
1. Update a `./input/publish_todo.txt` with a newly created TM id, like
   ```
   TM0001 TM0002 TM0003
   ```
1. Run `./scripts/publish.sh ~/MonlamAI/data/mitra-mt-en-bo-4`

## Running QC

1. cd into the `~/TM` directory
1. Update the `./input/qc_todo.txt` with the TM ids to be QCed, like
   ```
   TM0001 TM0002 TM0003
   ```
1. Then run `./scripts/qc.sh`

### What does qc script do?

- It will give assign a emoji number from 0️⃣-9️⃣ to each segment pair, which tells whether the segment pair is good or bad.
- 0️⃣ being the best and 9️⃣ being the worst.
- Segment pair with no asigned emoji is considered as the best.

Check out this example https://github.com/MonlamAI/TM2233/blob/main/TM2233-bo.txt
