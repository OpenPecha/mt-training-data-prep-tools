from unittest import mock

from op_mt_tools.qc.pipeline import RankMarker, SimilarityMetric
from op_mt_tools.qc.tm import get_similarity


def test_get_similarity():
    bo_sents = ["bo_text"]
    en_sents = ["en_text"]

    sim_scores = get_similarity(bo_sents, en_sents)

    assert isinstance(sim_scores, list)
    assert isinstance(sim_scores[0], float)
    assert sim_scores[0] >= 0.0
    assert len(sim_scores) == 1


@mock.patch("op_mt_tools.qc.pipeline.get_similarity")
def test_similarity_metric_0(mock_get_similarity):
    bo_sents = ["bo_text"]
    en_sents = ["en_text"]
    mock_get_similarity.return_value = [0.9]

    metric = SimilarityMetric(threshold=0.9, max_ranks=3)
    ranks, sim_scores, avg_rank, avg_sim_score = metric(bo_sents, en_sents)

    assert ranks[0] == 0
    assert avg_rank == 0


@mock.patch("op_mt_tools.qc.pipeline.get_similarity")
def test_similarity_metric_1(mock_get_similarity):
    bo_sents = ["bo_text", "bo_text", "bo_text"]
    en_sents = ["en_text", "en_text", "en_text"]
    mock_get_similarity.return_value = [0.3, 0.6, 0.8]

    metric = SimilarityMetric(threshold=0.9, max_ranks=3)
    ranks, sim_scores, avg_rank, avg_sim_score = metric(bo_sents, en_sents)

    assert ranks[0] == 3
    assert ranks[1] == 2
    assert ranks[2] == 1
    assert avg_rank == 2


@mock.patch("op_mt_tools.qc.pipeline.get_similarity")
def test_similarity_metric_2(mock_get_similarity):
    bo_sents = ["bo_text"]
    en_sents = ["en_text"]
    mock_get_similarity.return_value = [0.7404]

    metric = SimilarityMetric(threshold=0.8, max_ranks=3)
    ranks, sim_scores, avg_rank, avg_sim_score = metric(bo_sents, en_sents)

    assert ranks[0] == 1


def test_add_rank_marker():
    bo_sents = ["bo_text", "bo_text", "bo_text", "bo_text"]
    en_sents = ["en_text", "en_text", "en_text", "en_text"]
    ranks = [0, 1, 2, 3]

    rank_marker = RankMarker(markers=["0️⃣", "1️⃣", "2️⃣", "3️⃣"])

    ranked_bo_sents, ranked_en_sents = rank_marker.mark(bo_sents, en_sents, ranks)

    assert ranked_bo_sents[0] == "bo_text"
    assert ranked_en_sents[0] == "en_text"

    assert ranked_bo_sents[1] == "1️⃣ bo_text"
    assert ranked_en_sents[1] == "1️⃣ en_text"

    assert ranked_bo_sents[2] == "2️⃣ bo_text"
    assert ranked_en_sents[2] == "2️⃣ en_text"

    assert ranked_bo_sents[3] == "3️⃣ bo_text"
    assert ranked_en_sents[3] == "3️⃣ en_text"


def test_remove_rank_marker():
    bo_sents = ["0️⃣ bo_text", "1️⃣ bo_text", "2️⃣ bo_text", "3️⃣ bo_text"]
    en_sents = ["0️⃣ en_text", "1️⃣ en_text", "2️⃣ en_text", "3️⃣ en_text"]

    rank_marker = RankMarker(markers=["0️⃣", "1️⃣", "2️⃣", "3️⃣"])

    ranked_bo_sents, ranked_en_sents = rank_marker.remove(bo_sents, en_sents)

    assert ranked_bo_sents[0] == "bo_text"
    assert ranked_en_sents[0] == "en_text"

    assert ranked_bo_sents[1] == "bo_text"
    assert ranked_en_sents[1] == "en_text"

    assert ranked_bo_sents[2] == "bo_text"
    assert ranked_en_sents[2] == "en_text"

    assert ranked_bo_sents[3] == "bo_text"
    assert ranked_en_sents[3] == "en_text"
