import logging
import os
import sys
import time
from pathlib import Path

from gradio_client import Client
from gradio_client.utils import Status as JobStatus

params_json_fn = Path(sys.argv[1])

client = Client("openpecha/tibetan-aligner-api")

job = client.submit(
    params_json_fn,
    api_name="/align",
)

logging.info("Waiting for Alignment Job to start...")
while job.status().code != JobStatus.PROCESSING:
    time.sleep(1)
logging.info("Alignment Job started")
os._exit(0)
