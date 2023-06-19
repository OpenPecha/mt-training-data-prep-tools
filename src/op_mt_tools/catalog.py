import argparse
import csv
from dataclasses import asdict, dataclass

from tinydb import TinyDB

from op_mt_tools import config

catalog_path = config.ROOT_DIR / "data" / "catalog.json"


@dataclass
class Item:
    tm_id: str = ""
    direction: str = ""
    en_id: str = ""
    en_title: str = ""
    en_repo_url: str = ""
    bo_id: str = ""
    bo_title: str = ""
    bo_repo_url: str = ""
    oov_rate: float = 0.0
    qc_score: float = 0.0

    @classmethod
    def from_dict(cls, d):
        return Item(**d)

    def to_dict(self):
        return asdict(self)


class CatalogDB:
    def __init__(self, db_path):
        self._db_path = db_path
        self._db = TinyDB(catalog_path)

    def add_item(self, item: Item):
        self._db.insert(item.to_dict())


def read_csv(path):
    with open(path) as file:
        reader = csv.DictReader(file)
        yield from reader


@dataclass
class TextPair:
    direction: str = ""
    en_id: str = ""
    en_title: str = ""
    en_repo_url: str = ""
    bo_id: str = ""
    bo_title: str = ""
    bo_repo_url: str = ""

    @classmethod
    def from_dict(cls, d):
        return Item(**d)

    def to_dict(self):
        return asdict(self)


class ENBOCatalog:
    def __init__(self, path):
        self._path = path

    def get_rows(self):
        for row in read_csv(self._path):
            if not row["ཨང་།"]:
                continue
            yield row

    def get_cleaned_rows(self):
        for row in self.get_rows():
            if row["Clean"] == "TRUE" and row["QCed"] == "✔":
                yield row

    def get_cleaned_items(self):
        for row in self.get_cleaned_rows():
            yield TextPair(
                direction="enbo",
                en_id=row["EN Repo"],
                en_title=row["དབྱིན་མིང་། English Title"],
                en_repo_url=row["དྲ་ཐག Links (EN)"],
                bo_id=row["BO Repo"],
                bo_title=row["བོད་མིང་། Tibetan Title"],
                bo_repo_url=row["དྲ་ཐག Links (BO)"],
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--enbo_catalog", help="path to enbo catalog csv file")
    parser.add_argument("--boen_catalog", help="path to boen catalog csv file")

    args = parser.parse_args()

    enbo_catalog = ENBOCatalog(args.enbo_catalog)
    for cleaned_item in enbo_catalog.get_cleaned_items():
        print(cleaned_item)
