import argparse
from pathlib import Path

from op_mt_tools.cleanup import cleanup_en

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean up English text using OpenAI GPT"
    )
    parser.add_argument(
        "text_path",
        type=str,
        help="Path to the text.",
    )
    args = parser.parse_args()

    cleaned_fn = cleanup_en(Path(args.text_path))

    print("[INFO] Cleaned text saved to:", cleaned_fn)
