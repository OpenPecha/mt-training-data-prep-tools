import logging
import math
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
    def __init__(self, threshold=0.75, max_ranks=3):
        self.threshold = threshold
        self.max_ranks = max_ranks

    def compute_rank(self, sim_score: float) -> int:
        if sim_score >= self.threshold:
            return 0
        else:
            return math.ceil((self.threshold - sim_score) / self.max_ranks * 10)

    def compute_overall_rank(self, sim_scores: List[float]) -> Tuple[int, float]:
        sim_scores_avg = sum(sim_scores) / len(sim_scores)
        return self.compute_rank(sim_scores_avg), sim_scores_avg

    def __call__(
        self, bo_sents: List[str], en_sents: List[str]
    ) -> Tuple[List[int], List[float], int, float]:
        sim_scores = get_similarity(bo_sents, en_sents)
        sim_scores_ranks = [self.compute_rank(score) for score in sim_scores]
        avg_rank, avg_sim_score = self.compute_overall_rank(sim_scores)
        return sim_scores_ranks, sim_scores, avg_rank, avg_sim_score


class RankMarker:
    def __init__(self, markers: List[str] = []):
        if markers:
            self.rank_markers = markers
        else:
            self.rank_markers = [
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
            ]

    def __remove_marker(self, sent: str) -> str:
        for marker in self.rank_markers:
            sent = sent.replace(marker, "").strip()
        return sent

    def remove(
        self, bo_sents: List[str], en_sents: List[str]
    ) -> Tuple[List[str], List[str]]:
        bo_sents = [self.__remove_marker(sent) for sent in bo_sents]
        en_sents = [self.__remove_marker(sent) for sent in en_sents]
        return bo_sents, en_sents

    def mark(
        self, bo_sents: List[str], en_sents: List[str], ranks: List[int]
    ) -> Tuple[List[str], List[str]]:
        ranked_bo_sents = []
        ranked_en_sents = []
        for rank, bo_sent, en_sent in zip(ranks, bo_sents, en_sents):
            rank_marker = "" if rank == 0 else f"{self.rank_markers[rank]} "
            ranked_bo_sents.append(f"{rank_marker}{bo_sent.strip()}")
            ranked_en_sents.append(f"{rank_marker}{en_sent.strip()}")

        return ranked_bo_sents, ranked_en_sents


def save_review(tm_path: Path, bo_sents: List[str], en_sents: List[str]):
    tm_id = tm_path.name
    bo_text_fn = tm_path / f"{tm_id}-bo.txt"
    en_text_fn = tm_path / f"{tm_id}-en.txt"
    bo_text_fn.write_text("\n".join(bo_sents), encoding="utf-8")
    en_text_fn.write_text("\n".join(en_sents), encoding="utf-8")


def log_ranked_sents(
    bo_sents: List[str], en_sents: List[str], sim_scores: List[float], ranks: List[int]
):
    for bo_sent, en_sent, sim_score, rank in zip(bo_sents, en_sents, sim_scores, ranks):
        logging.info(f"{rank} {sim_score} {bo_sent} ||| {en_sent}")


def run_pipeline(tms_path: Path, tm_ids: List[str], disable_push=False, verbose=False):
    assert tms_path.exists()
    for tm_path in tms_path.iterdir():
        if tm_path.name not in tm_ids:
            continue
        logging.info(f"Running QC on {tm_path.name}")
        metric = SimilarityMetric()
        rank_marker = RankMarker()
        bo_sents, en_sents = get_sentence_pairs(tm_path)
        bo_sents, en_sents = rank_marker.remove(bo_sents, en_sents)
        ranks, sim_scores, tm_rank, tm_avg_sim_score = metric(bo_sents, en_sents)
        ranked_bo_sents, ranked_en_sents = rank_marker.mark(bo_sents, en_sents, ranks)
        if verbose:
            log_ranked_sents(ranked_bo_sents, ranked_en_sents, sim_scores, ranks)
        save_review(tm_path, ranked_bo_sents, ranked_en_sents)
        logging.info(
            f"{tm_path.name} rank: {tm_rank}, avg sim score: {tm_avg_sim_score}"
        )
        if not disable_push:
            commit_and_push(tm_path, "add QC review")
        break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add text pairs to collection.")
    parser.add_argument(
        "tms_path",
        type=str,
        help="Path to list of TMs to run QC on.",
    )
    parser.add_argument(
        "--tm_ids",
        type=str,
        nargs="+",
        help="TM ids to run QC on.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="whether to print ranked sentences",
    )
    parser.add_argument(
        "--disable-push",
        action="store_true",
        help="whether to disable push to github",
    )

    args = parser.parse_args()

    run_pipeline(
        Path(args.tms_path),
        tm_ids=args.tm_ids,
        disable_push=args.disable_push,
        verbose=args.verbose,
    )
