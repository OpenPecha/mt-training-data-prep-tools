import logging
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from .. import config
from ..github_utils import commit_and_push
from .tm import get_sentence_pairs, get_similarity

# Configure the logging settings
log_fn = config.LOGGING_PATH / f"qc-{datetime.now()}.log"
logging.basicConfig(
    filename=str(log_fn),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class SimilarityMetric:
    def __init__(self, threshold=0.8, max_ranks=3):
        self.threshold = threshold
        self.max_ranks = max_ranks

    def compute_rank(self, sim_score: float) -> int:
        sim_score = max(sim_score, 0.0)
        if sim_score >= self.threshold:
            return 0
        else:
            return math.ceil((self.threshold - sim_score) / self.max_ranks * 10)

    def compute_overall_rank(self, sim_scores: List[float]) -> int:
        sim_scores = [max(sim_score, 0.0) for sim_score in sim_scores]
        sim_scores_avg = sum(sim_scores) / len(sim_scores)
        return self.compute_rank(sim_scores_avg)

    def __call__(
        self, bo_sents: List[str], en_sents: List[str]
    ) -> Tuple[List[int], int]:
        sim_scores = get_similarity(bo_sents, en_sents)
        sim_scores_ranks = [self.compute_rank(score) for score in sim_scores]
        overall_rank = self.compute_overall_rank(sim_scores)
        return sim_scores_ranks, overall_rank


def add_rank_marker(
    bo_sents: List[str], en_sents: List[str], ranks: List[int]
) -> Tuple[List[str], List[str]]:
    rank_markers = [
        "0️⃣",
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "🔟",
    ]
    ranked_bo_sents = []
    ranked_en_sents = []
    for rank, bo_sent, en_sent in zip(ranks, bo_sents, en_sents):
        rank_marker = "" if rank == 0 else f"{rank_markers[rank]} "

        # skip if already marked
        if bo_sent[0] in rank_markers:
            rank_marker = ""

        ranked_bo_sents.append(f"{rank_marker}{bo_sent.strip()}")
        ranked_en_sents.append(f"{rank_marker}{en_sent.strip()}")

    return ranked_bo_sents, ranked_en_sents


def save_review(tm_path: Path, bo_sents: List[str], en_sents: List[str]):
    tm_id = tm_path.name
    bo_text_fn = tm_path / f"{tm_id}-bo.txt"
    en_text_fn = tm_path / f"{tm_id}-en.txt"
    bo_text_fn.write_text("\n".join(bo_sents), encoding="utf-8")
    en_text_fn.write_text("\n".join(en_sents), encoding="utf-8")


def run_pipeline(input_path: Path):
    for tm_path in input_path.iterdir():
        logging.info(f"QC  on {tm_path.name}")
        bo_sents, en_sents = get_sentence_pairs(tm_path)
        metric = SimilarityMetric()
        ranks, tm_rank = metric(bo_sents, en_sents)
        reviewed_bo_sents, reviewed_en_sents = add_rank_marker(
            bo_sents, en_sents, ranks
        )
        save_review(tm_path, reviewed_bo_sents, reviewed_en_sents)
        logging.info(f"{tm_path.name} rank: {tm_rank}")
        commit_and_push(tm_path, "add QC review")
        break


if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    assert input_path.exists()
    run_pipeline(input_path)
