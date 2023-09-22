from pathlib import Path


def parse_ids(file):
    lines = Path(file).read_text().splitlines()
    if len(lines) == 1:
        ids = lines[0].split()
    else:
        ids = [line.strip() for line in lines]
    return set(ids)


def print_union(ids_a, ids_b):

    print("\n".join(sorted(ids_a.union(ids_b))))


def print_intersect(ids_a, ids_b):
    print("\n".join(sorted(ids_a.intersection(ids_b))))


def print_diff(ids_a, ids_b):
    print("\n".join(sorted(ids_a.difference(ids_b))))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="check ids for overlap or missing")
    parser.add_argument(
        "file_a",
        type=str,
        help="file_a with ids",
    )
    parser.add_argument(
        "file_b",
        type=str,
        help="file_b with ids",
    )
    parser.add_argument(
        "--op",
        help="Operation to perform (Union, Intersect, Diff)",
    )

    args = parser.parse_args()

    ids_a = parse_ids(args.file_a)
    ids_b = parse_ids(args.file_b)

    if args.op == "Union":
        print_union(ids_a, ids_b)
    elif args.op == "Intersect":
        print_intersect(ids_a, ids_b)
    elif args.op == "Diff":
        print_diff(ids_a, ids_b)
    else:
        parser.print_help()
