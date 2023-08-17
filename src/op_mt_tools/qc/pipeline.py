import math
import sys
from pathlib import Path
from typing import List, Tuple

from .tm import get_sentence_pairs


class CharLenRatioAvgMetric:
    def __init__(self, avg_ratio=1.67, upper_bound=2, lower_bound=0.2):
        self.avg_ratio = avg_ratio
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound

    @staticmethod
    def get_pairs_char_len_ratio(bo_sents: List[str], en_sents: List[str]):
        char_len_ratios = [
            len(en_sent) / len(bo_sent) for bo_sent, en_sent in zip(bo_sents, en_sents)
        ]
        return char_len_ratios

    def compute_rank(self, ratio: float) -> int:
        ratio_norm = ratio / self.avg_ratio
        if self.lower_bound <= ratio_norm <= self.upper_bound:
            return 1
        elif ratio_norm < self.lower_bound:
            return 2
        else:
            return math.ceil(ratio_norm)

    def __call__(self, bo_sents: List[str], en_sents: List[str]) -> List[int]:
        char_len_ratios = self.get_pairs_char_len_ratio(bo_sents, en_sents)
        return [self.compute_rank(ratio) for ratio in char_len_ratios]


def add_notice_marker(
    bo_sents: List[str], en_sents: List[str], ranks: List[int], notice_sign="⚠️"
) -> Tuple[List[str], List[str]]:
    reviewed_bo_sents = []
    reviewed_en_sents = []
    for rank, bo_sent, en_sent in zip(ranks, bo_sents, en_sents):
        if rank == 1:
            marker = ""
        else:
            marker = notice_sign * rank
        reviewed_bo_sents.append(f"{marker} {bo_sent}")
        reviewed_en_sents.append(f"{marker} {en_sent}")

    return reviewed_bo_sents, reviewed_en_sents


def save_review(tm_path: Path, bo_sents: List[str], en_sents: List[str]):
    tm_id = tm_path.name
    bo_text_fn = tm_path / f"{tm_id}-bo.txt"
    en_text_fn = tm_path / f"{tm_id}-en.txt"
    bo_text_fn.write_text("\n".join(bo_sents), encoding="utf-8")
    en_text_fn.write_text("\n".join(en_sents), encoding="utf-8")


def run_pipeline(input_path: Path):
    for tm_path in input_path.iterdir():
        print(f"Reviewing {tm_path.name}...")
        bo_sents, en_sents = get_sentence_pairs(tm_path)
        metric = CharLenRatioAvgMetric()
        char_len_ratio_ranks = metric(bo_sents, en_sents)
        reviewed_bo_sents, reviewed_en_sents = add_notice_marker(
            bo_sents, en_sents, char_len_ratio_ranks
        )
        save_review(tm_path, reviewed_bo_sents, reviewed_en_sents)
        break


if __name__ == "__main__":
    input_path = Path(sys.argv[1])
    assert input_path.exists()
    run_pipeline(input_path)
