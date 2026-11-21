from services.batch_scorer import score_excel

summary = score_excel(
    "data/sample_businesses.xlsx",
    "data/scored_output.xlsx"
)

print("Saved data/scored_output.xlsx")
print("Summary:", summary)
