import csv
import random
import sys
from pathlib import Path
from typing import Dict, List

model = None


def get_model():
    from sentence_transformers import SentenceTransformer

    global model
    model_path = "buddhist-nlp/bod-eng-similarity"
    if model is None:
        model = SentenceTransformer(model_path)
    return model


def get_embedding(sentences):
    model = get_model()
    return model.encode(sentences, convert_to_tensor=True)


def get_similarity(sentences1, sentences2):
    from sentence_transformers import util

    embeddings1 = get_embedding(sentences1)
    embeddings2 = get_embedding(sentences2)
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    return cosine_scores


def get_text_paths(tm_path: Path) -> Dict[str, Path]:
    text_paths = {}
    for fn in tm_path.iterdir():
        if not fn.name.endswith(".txt"):
            continue

        lang_code = fn.stem.split("-")[1]
        text_paths[lang_code] = fn
    return text_paths


def get_sentence_pairs(tm_path: Path):
    """Get sentence pair from text pair path."""
    text_paths = get_text_paths(tm_path)
    bo_sents = text_paths["bo"].read_text(encoding="utf-8").splitlines()
    en_sents = text_paths["en"].read_text(encoding="utf-8").splitlines()
    return bo_sents, en_sents[: len(bo_sents)]


def get_sentence_pairs_random_sample(tm_path: Path, n=100):
    bo_sents, en_sents = get_sentence_pairs(tm_path)
    pair_idxs_sample = sorted(random.sample(range(len(bo_sents)), n))
    bo_sents_sample = [bo_sents[i] for i in pair_idxs_sample]
    en_sents_sample = [en_sents[i] for i in pair_idxs_sample]
    return pair_idxs_sample, bo_sents_sample, en_sents_sample


def get_sentence_pairs_sim(tm_path: Path):
    bo_sents, en_sents = get_sentence_pairs(tm_path)
    cosine_scores = get_similarity(bo_sents, en_sents)
    return list(range(len(bo_sents))), bo_sents, en_sents, cosine_scores


def get_sentence_pairs_sim_sample(tm_path: Path):
    line_idxs, bo_sents, en_sents = get_sentence_pairs_random_sample(tm_path)
    cosine_scores = get_similarity(bo_sents, en_sents)
    return line_idxs, bo_sents, en_sents, cosine_scores


def get_sentence_pairs_char_len_ratio(bo_sents: List[str], en_sents: List[str]):
    char_len_ratios = [
        len(en_sent) / len(bo_sent) for bo_sent, en_sent in zip(bo_sents, en_sents)
    ]
    return char_len_ratios


def save_to_csv(
    line_idxs, bo_sents, en_sents, cosine_scores, char_len_ratios, csv_path
):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            ["line_num", "sim_score", "char_len_ratio", "bo_sent", "en_sent"]
        )
        for i in range(len(bo_sents)):
            csv_writer.writerow(
                [
                    line_idxs[i] + 1,
                    f"{cosine_scores[i][i]:.4f}",
                    f"{char_len_ratios[i]:.4f}",
                    bo_sents[i],
                    en_sents[i],
                ]
            )
    print(f"Saved to {csv_path}")


if __name__ == "__main__":
    tm_id = sys.argv[1]
    data_path = Path("data") / "qc"
    assert data_path.exists()
    tm_path = data_path / tm_id
    assert tm_path.exists()
    csv_path = data_path / f"{tm_path.name}_qc.csv"

    line_idxs, bo_sents, en_sents, cosine_scores = get_sentence_pairs_sim(tm_path)
    char_len_ratios = get_sentence_pairs_char_len_ratio(bo_sents, en_sents)
    save_to_csv(line_idxs, bo_sents, en_sents, cosine_scores, char_len_ratios, csv_path)
