import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.batch_scorer import score_excel

summary = score_excel(
    os.path.join(ROOT, "data", "sample_businesses.xlsx"),
    os.path.join(ROOT, "data", "scored_output.xlsx")
)

print("Saved data/scored_output.xlsx")
print("Summary:", summary)
