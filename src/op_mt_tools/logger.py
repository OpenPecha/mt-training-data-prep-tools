import logging

from . import config


def setup_logger(name):
    log_fn = config.LOGGING_PATH / f"{name}.log"
    logging.basicConfig(
        filename=str(log_fn),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return log_fn
