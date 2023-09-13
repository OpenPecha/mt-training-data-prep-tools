import logging

from . import config


def setup_logger(name):
    log_fn = config.LOGGING_PATH / f"{name}.log"
    if log_fn.exists():
        log_fn.unlink()
    logging.basicConfig(
        filename=str(log_fn),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_fn
