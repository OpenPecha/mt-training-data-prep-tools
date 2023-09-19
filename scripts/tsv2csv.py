import csv
import sys


# Function to convert TSV to CSV
def tsv_to_csv(input_file, output_file):
    with open(input_file, newline="") as tsvfile, open(
        output_file, "w", newline=""
    ) as csvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        for row in tsvreader:
            csvwriter.writerow(row)


if __name__ == "__main__":
    input_file = sys.argv[1]  # TSV file
    output_file = sys.argv[2]  # CSV file

    tsv_to_csv(input_file, output_file)
    print(f"Conversion from '{input_file}' to '{output_file}' is complete.")
