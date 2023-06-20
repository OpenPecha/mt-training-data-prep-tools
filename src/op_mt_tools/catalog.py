import argparse
import csv
import os
from dataclasses import asdict, dataclass
from typing import Optional

import requests
from tinydb import Query, TinyDB

from op_mt_tools import config

catalog_path = config.ROOT_DIR / "data" / "catalog.json"
catalog_csv_output_path = config.ROOT_DIR / "data" / "catalog.csv"


@dataclass
class TMCatalogItem:
    tm_id: str = ""
    direction: str = ""
    created_at: Optional[str] = None
    en_id: str = ""
    en_title: str = ""
    en_repo_url: str = ""
    bo_id: str = ""
    bo_title: str = ""
    bo_repo_url: str = ""
    manual_qced: bool = False
    oov_rate: Optional[float] = None
    qc_score: Optional[float] = None
    cleaned: Optional[float] = None

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
        else:
            self._db.update(item.to_dict(), self.tm_query.tm_id == item.tm_id)

    def get_item(self, tm_id):
        item = self._db.get(self.tm_query.tm_id == tm_id)
        if item:
            return TMCatalogItem.from_dict(item)
        else:
            return None

    def get_items(self):
        for item in self._db.all():
            yield TMCatalogItem.from_dict(item)

    def get_tm_created_items(self):
        for item in self._db.search(self.tm_query.created_at):
            yield TMCatalogItem.from_dict(item)


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


def get_repo_created_at(org: str, repo: str):
    print("called", repo)
    url = f"https://api.github.com/repos/{org}/{repo}"
    access_token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        created_at = repo_data["created_at"]
        return created_at
    else:
        return None


def get_tm_created_at(tm_id, bo_repo_url):
    if not bo_repo_url:
        return None
    org = bo_repo_url.split("/")[3]
    return get_repo_created_at(org, tm_id)


@dataclass
class TextPair:
    direction: str = ""
    en_id: str = ""
    en_title: str = ""
    en_repo_url: str = ""
    bo_id: str = ""
    bo_title: str = ""
    bo_repo_url: str = ""
    cleaned: bool = False

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

    def _is_cleaned(self, row):
        return row["Clean"] == "TRUE" and row["QCed"] == "✔"

    def get_cleaned_rows(self):
        for row in self.get_rows():
            if self._is_cleaned(row):
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
            cleaned=self._is_cleaned(row),
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

    def is_cleaned(self, row):
        return row["Done"] == "TRUE" and row["QCed"] == "✔"

    def get_cleaned_rows(self):
        for row in self.get_rows():
            if self.is_cleaned(row):
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
            cleaned=self.is_cleaned(row),
        )

    def get_cleaned_items(self):
        for row in self.get_cleaned_rows():
            yield self._to_text_pair(row)

    def get_items(self):
        for row in self.get_rows():
            yield self._to_text_pair(row)


def run_import(args):
    print(f"[INFO] Importing to TM Catalog at {args.catalog_path}")

    enbo_catalog = ENBOCatalog(args.enbo_path)
    boen_catalog = BOENCatalog(args.boen_path)
    catalog_db = TMCatalogDB(args.catalog_path)

    if args.cleaned:
        text_pairs = list(enbo_catalog.get_cleaned_items()) + list(
            boen_catalog.get_cleaned_items()
        )
    else:
        text_pairs = list(enbo_catalog.get_items()) + list(boen_catalog.get_items())
    for text_pair in text_pairs:
        tm_id = f"TM{text_pair.en_id[2:]}"
        tm_item = catalog_db.get_item(tm_id)
        new_tm_item = TMCatalogItem(
            tm_id=tm_id,
            direction=text_pair.direction,
            en_id=text_pair.en_id,
            en_title=text_pair.en_title,
            en_repo_url=text_pair.en_repo_url,
            bo_id=text_pair.bo_id,
            bo_title=text_pair.bo_title,
            bo_repo_url=text_pair.bo_repo_url,
        )

        if not new_tm_item.en_repo_url or not new_tm_item.bo_repo_url:
            catalog_db.add_item(new_tm_item)
            continue

        # reuse created_at if exists
        if tm_item:
            if not new_tm_item.created_at and tm_item.created_at:
                new_tm_item.created_at = tm_item.created_at
            else:
                new_tm_item.created_at = get_tm_created_at(
                    tm_id, new_tm_item.bo_repo_url
                )
        else:
            new_tm_item.created_at = get_tm_created_at(tm_id, new_tm_item.bo_repo_url)

        catalog_db.add_item(new_tm_item)

    print(f"[INFO] Imported {len(text_pairs)} items")


def run_export(args):
    catalog_db = TMCatalogDB(args.catalog_path)
    tm_catalog_items = [item.to_dict() for item in catalog_db.get_tm_created_items()]
    tm_catalog_items.sort(key=lambda x: x["tm_id"])
    write_dict_to_csv(tm_catalog_items, args.output_path)
    print("[INFO] TM catalog exported to", args.output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cli for managing translation memory catalog"
    )
    subparsers = parser.add_subparsers(dest="command")

    ###############
    # Import Args #
    ###############
    import_ = subparsers.add_parser("import", help="import catalog from csv files")
    import_.add_argument("enbo_path", help="path to enbo catalog csv file")
    import_.add_argument("boen_path", help="path to boen catalog csv file")
    import_.add_argument("--cleaned", help="only cleaned items", action="store_true")
    import_.add_argument(
        "--catalog_path",
        help="path to catalog json file",
        default=catalog_path,
    )
    import_.add_argument("--update", help="update existing items", action="store_true")

    ###############
    # Export Args #
    ###############
    export = subparsers.add_parser("export", help="export catalog to csv file")
    export.add_argument(
        "--catalog_path",
        help="path to catalog json file",
        default=catalog_path,
    )
    export.add_argument(
        "--output_path",
        help="path to output catalog json file",
        default=catalog_csv_output_path,
    )

    #################
    # Validate Args #
    #################
    validate = subparsers.add_parser("check", help="check catalog for correctness")

    args = parser.parse_args()
    if args.command == "import":
        run_import(args)
    elif args.command == "export":
        run_export(args)
