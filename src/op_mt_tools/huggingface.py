import os
import time

from huggingface_hub import SpaceStage, get_space_runtime, restart_space

space_id = os.environ["HF_TIB_ALIGNER_ID"]
token = os.environ["HF_TOKEN"]


def start_aligner_service(id_: str = space_id, token: str = token):
    current_stage = get_space_runtime(id_, token=token).stage
    if current_stage == SpaceStage.RUNNING.value:
        print("[INFO] Space is already running!")
        return

    space_runtime = restart_space(space_id, token=token)
    print("[INFO] Waiting for the space to be ready...")
    current_stage = space_runtime.stage
    while current_stage != SpaceStage.RUNNING.value:
        current_stage = get_space_runtime(space_id, token=token).stage
        time.sleep(5)
    print("[INFO] Space is ready!")
