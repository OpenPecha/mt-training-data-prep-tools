import re
import sys

from .. import config


def get_qc_logs():
    for log_path in config.LOGGING_PATH.iterdir():
        if not log_path.name.endswith(".log") or not log_path.name.startswith("qc-"):
            continue
        yield log_path.read_text(encoding="utf-8")


def parse_rank():
    for log in get_qc_logs():
        pattern = r"TM(\d+)\s+rank: (\d+), avg sim score: ([\d.]+)"
        matches = re.findall(pattern, log)
        if not matches:
            continue
        for match in matches:
            tm_id, rank, avg_sim_score = match
            yield tm_id, rank, avg_sim_score


def parse_failed_download():
    for log in get_qc_logs():
        pattern = r"ERROR - Error in downloading (TM\d+)"
        matches = re.findall(pattern, log)
        if not matches:
            continue
        for match in matches:
            tm_id = match
            yield tm_id


if __name__ == "__main__":
    if len(sys.argv) == 2:
        command = sys.argv[1]
    else:
        command = "rank"

    if command == "error":
        for tm_id in parse_failed_download():
            print(tm_id)
    elif command == "rank":
        for tm_id, rank, avg_sim_score in parse_rank():
            print(f"{tm_id},{rank},{avg_sim_score}")
