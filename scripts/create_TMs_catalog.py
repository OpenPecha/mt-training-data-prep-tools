import argparse
import csv


# Read CSV file
def read_csv(file_path):
    with open(file_path) as file:
        reader = csv.reader(file)
        yield from reader


# Write CSV file
def write_csv(file_path, data):
    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)


def get_tm_row(row):
    if row[0] == "EN":
        return ["TM", "Direction"]
    else:
        return [f"TM{row[0][2:]}", row[2]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfer ownership of a repository from one organization to another."
    )
    parser.add_argument(
        "input",
        help="input csv file",
    )
    parser.add_argument(
        "--output", help="output csv file", default="./data/tms_catalog.csv"
    )

    args = parser.parse_args()

    data = read_csv(args.input)
    tms = [get_tm_row(row) for row in data]
    write_csv(args.output, tms)
