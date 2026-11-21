"""Score a CSV or Excel portfolio locally, without starting the API server."""

import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from services.batch_scorer import score_excel


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python offline/offline_score.py <input.xlsx|input.csv> [output.xlsx|output.csv]")
        raise SystemExit(2)

    input_file = os.path.abspath(sys.argv[1])
    if not os.path.isfile(input_file):
        print(f"File not found: {input_file}")
        raise SystemExit(2)

    extension = os.path.splitext(input_file)[1].lower()
    if extension not in {".xlsx", ".csv"}:
        print("Input must be a .xlsx or .csv file.")
        raise SystemExit(2)

    if len(sys.argv) == 3:
        output_file = os.path.abspath(sys.argv[2])
    else:
        output_file = os.path.join(repo_root, "offline", f"scored_output{extension}")

    summary = score_excel(input_file, output_file)
    print(f"Scored {summary['records']} businesses locally.")
    print(f"Approved: {summary['approved']} | Rejected: {summary['rejected']} | Average score: {summary['average_score']}/100")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
