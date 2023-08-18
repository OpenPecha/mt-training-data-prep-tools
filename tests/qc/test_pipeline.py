from unittest import mock

from op_mt_tools.qc.pipeline import SimilarityMetric, add_notice_marker
from op_mt_tools.qc.tm import get_similarity


def test_get_similarity():
    bo_sents = ["bo_text"]
    en_sents = ["en_text"]
    cosine_scores = get_similarity(bo_sents, en_sents)

    assert isinstance(cosine_scores, list)
    assert isinstance(cosine_scores[0], float)
    assert len(cosine_scores) == 1


@mock.patch("op_mt_tools.qc.pipeline.get_similarity")
def test_similarity_metric(mock_get_similarity):
    bo_sents = ["bo_text"]
    en_sents = ["en_text"]
    mock_get_similarity.return_value = [0.9]

    metric = SimilarityMetric(threshold=0.9, max_ranks=3)
    ranks, overall_rank = metric(bo_sents, en_sents)

    assert ranks[0] == 0
    assert overall_rank == 0


@mock.patch("op_mt_tools.qc.pipeline.get_similarity")
def test_similarity_metric_1(mock_get_similarity):
    bo_sents = ["bo_text", "bo_text", "bo_text"]
    en_sents = ["en_text", "en_text", "en_text"]
    mock_get_similarity.return_value = [0.3, 0.6, 0.8]

    metric = SimilarityMetric(threshold=0.9, max_ranks=3)
    ranks, overall_rank = metric(bo_sents, en_sents)

    assert ranks[0] == 3
    assert ranks[1] == 2
    assert ranks[2] == 1
    assert overall_rank == 2


def test_add_rank_marker():
    bo_sents = ["bo_text", "bo_text", "bo_text"]
    en_sents = ["en_text", "en_text", "en_text"]
    ranks = [3, 2, 1]

    reviewed_bo_sents, reviewed_en_sents = add_notice_marker(bo_sents, en_sents, ranks)
