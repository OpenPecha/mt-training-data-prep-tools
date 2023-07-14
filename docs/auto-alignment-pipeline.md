# Running Auto Alignment

## 1. EN Cleanup

**Input**
`input.txt`

```
EN0504 EN0702 EN0709 EN0710 EN0723 EN0725 EN0726 EN0728 EN0746 EN0747 EN0751
```

**Run Command:**

 ```bash
python -m op_mt_tools.cli.cleanup_en batch_cleanup $(cat input.txt)
```


## 2. Start Aligner

1. Go to https://github.com/OpenPecha-Data/C1A81F448


2. Start the Aligner
- triger start
<img width="1432" alt="Screenshot 2023-05-29 at 4 18 01 PM" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/6ea2071a-fd1c-4590-9180-5ff495672655">

- check if the aligner is running [here](https://huggingface.co/spaces/openpecha/tibetan-aligner-api)

3. Run Aligner
- Set input:
  <img width="1255" alt="run_aligner_input" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/9fea13e8-1c83-446f-a96d-cd92fbbaf9f9">
- Run Alinger
  <img width="1762" alt="Run Aligner" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/b5a1170c-8229-487b-9c90-62447fac7038">
- Check log if the aligner running properly from [here](https://huggingface.co/spaces/openpecha/tibetan-aligner-api)
  <img width="1467" alt="Screenshot 2023-05-29 at 4 24 05 PM" src="https://github.com/OpenPecha/mt-training-data-prep-tools/assets/16164304/e46df67e-3f2f-4084-a7fa-8de8701474d7">
