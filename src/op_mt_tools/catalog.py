import argparse
import csv
from dataclasses import asdict, dataclass
from typing import Optional

from tinydb import Query, TinyDB

from op_mt_tools import config

catalog_path = config.ROOT_DIR / "data" / "catalog.json"
catalog_csv_output_path = config.ROOT_DIR / "data" / "catalog.csv"


@dataclass
class TMCatalogItem:
    tm_id: str = ""
    direction: str = ""
    en_id: str = ""
    en_title: str = ""
    en_repo_url: str = ""
    bo_id: str = ""
    bo_title: str = ""
    bo_repo_url: str = ""
    oov_rate: Optional[float] = None
    qc_score: Optional[float] = None

    @classmethod
    def from_dict(cls, d):
        return TMCatalogItem(**d)

    def to_dict(self):
        return asdict(self)


class TMCatalogDB:
    def __init__(self, db_path):
        self._db_path = db_path
        self._db = TinyDB(catalog_path)
        self.tm_query = Query()

    def _exists(self, tm_id):
        return self._db.contains(self.tm_query.tm_id == tm_id)

    def add_item(self, item: TMCatalogItem):
        if not self._exists(item.tm_id):
            self._db.insert(item.to_dict())


def read_csv(path):
    with open(path) as file:
        reader = csv.DictReader(file)
        yield from reader


def write_dict_to_csv(data, path):
    fieldnames = data[0].keys() if data else []
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


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
        return TextPair(**d)

    def to_dict(self):
        return asdict(self)


def clean_title(title):
    return title.strip().replace("\t", " ").replace("\n", "")


class ENBOCatalog:
    def __init__(self, path):
        self._path = path
        self.direction = "enbo"

    def get_rows(self):
        for row in read_csv(self._path):
            if not row["ཨང་།"]:
                continue
            yield row

    def get_cleaned_rows(self):
        for row in self.get_rows():
            if row["Clean"] == "TRUE" and row["QCed"] == "✔":
                yield row

    def _to_text_pair(self, row):
        return TextPair(
            direction=self.direction,
            en_id=row["EN Repo"].strip(),
            en_title=clean_title(row["དབྱིན་མིང་། English Title"]),
            en_repo_url=row["དྲ་ཐག Links (EN)"].strip(),
            bo_id=row["BO Repo"].strip(),
            bo_title=clean_title(row["བོད་མིང་། Tibetan Title"]),
            bo_repo_url=row["དྲ་ཐག Links (BO)"].strip(),
        )

    def get_cleaned_items(self):
        for row in self.get_cleaned_rows():
            yield self._to_text_pair(row)

    def get_items(self):
        for row in self.get_rows():
            yield self._to_text_pair(row)


class BOENCatalog:
    def __init__(self, path):
        self._path = path
        self.direction = "boen"

    def get_rows(self):
        for row in read_csv(self._path):
            if not row["Tittle"] or row["Tittle"].isdigit():
                continue
            yield row

    def get_cleaned_rows(self):
        for row in self.get_rows():
            if row["Done"] == "TRUE" and row["QCed"] == "✔":
                yield row

    def _to_text_pair(self, row):
        return TextPair(
            direction=self.direction,
            en_id=row["EN Repo"].strip(),
            en_title=clean_title(row["Tittle"]),
            en_repo_url=row["Link"].strip(),
            bo_id=row["BO Repo"].strip(),
            bo_title=clean_title(row["Bo title-0"]),
            bo_repo_url=row["Link-0"].strip(),
        )

    def get_cleaned_items(self):
        for row in self.get_cleaned_rows():
            yield self._to_text_pair(row)

    def get_items(self):
        for row in self.get_rows():
            yield self._to_text_pair(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("enbo_path", help="path to enbo catalog csv file")
    parser.add_argument("boen_path", help="path to boen catalog csv file")
    parser.add_argument(
        "--only_cleaned", help="only cleaned items", action="store_true"
    )
    parser.add_argument(
        "--output_path",
        help="path to output catalog json file",
        default=catalog_csv_output_path,
    )

    args = parser.parse_args()
    enbo_catalog = ENBOCatalog(args.enbo_path)
    boen_catalog = BOENCatalog(args.boen_path)
    catalog_db = TMCatalogDB(catalog_path)

    if args.only_cleaned:
        text_pairs = list(enbo_catalog.get_cleaned_items()) + list(
            boen_catalog.get_cleaned_items()
        )
        print("cleaned", len(text_pairs))
    else:
        text_pairs = list(enbo_catalog.get_items()) + list(boen_catalog.get_items())
        print("uncleaned", len(text_pairs))
    tm_catalog_items = []
    for text_pair in text_pairs:
        tm_catalog_item = TMCatalogItem(
            tm_id=f"TM{text_pair.en_id[2:]}",
            direction=text_pair.direction,
            en_id=text_pair.en_id,
            en_title=text_pair.en_title,
            en_repo_url=text_pair.en_repo_url,
            bo_id=text_pair.bo_id,
            bo_title=text_pair.bo_title,
            bo_repo_url=text_pair.bo_repo_url,
        )

        tm_catalog_items.append(tm_catalog_item.to_dict())
        catalog_db.add_item(tm_catalog_item)

    tm_catalog_items.sort(key=lambda x: x["tm_id"])
    write_dict_to_csv(tm_catalog_items, args.output_path)
