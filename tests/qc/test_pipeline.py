from op_mt_tools.qc.pipeline import CharLenRatioAvgMetric, add_notice_marker


def test_char_len_ratio_avg_metric_1():
    bo_sents = ["*" * 2]
    en_sents = ["*" * 4]
    metric = CharLenRatioAvgMetric(avg_ratio=1, upper_bound=2, lower_bound=0)
    ranks = metric(bo_sents, en_sents)

    assert ranks[0] == 1


def test_char_len_ratio_avg_metric_2():
    bo_sents = ["*" * 2]
    en_sents = ["*" * 1]
    metric = CharLenRatioAvgMetric(avg_ratio=1, upper_bound=2, lower_bound=0)
    ranks = metric(bo_sents, en_sents)

    assert ranks[0] == 1


def test_char_len_ratio_avg_metric_3():
    bo_sents = ["*" * 2]
    en_sents = ["*" * 10]
    metric = CharLenRatioAvgMetric(avg_ratio=1, upper_bound=2, lower_bound=0)
    ranks = metric(bo_sents, en_sents)

    assert ranks[0] == 5


def test_add_notice_marker():
    bo_sents = ["a"]
    en_sents = ["a"]
    ranks = [1]
    notice_sign = "*"

    marked_bo_sents, marked_en_sents = add_notice_marker(
        bo_sents, en_sents, ranks, notice_sign=notice_sign
    )

    assert marked_bo_sents[0][0] != notice_sign
    assert marked_en_sents[0][0] != notice_sign


def test_add_notice_marker_2():
    bo_sents = ["a"]
    en_sents = ["a"]
    ranks = [5]
    notice_sign = "*"

    marked_bo_sents, marked_en_sents = add_notice_marker(
        bo_sents, en_sents, ranks, notice_sign=notice_sign
    )

    assert marked_bo_sents[0].startswith(notice_sign * ranks[0])
    assert marked_en_sents[0].startswith(notice_sign * ranks[0])
