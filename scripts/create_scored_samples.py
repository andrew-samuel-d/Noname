import os
import sys
import csv
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.predictor import predict_score

base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
in_csv = os.path.join(base_dir, "sample_100_businesses_input.csv")
out_csv = os.path.join(base_dir, "sample_100_businesses_scored.csv")
out_xlsx = os.path.join(base_dir, "sample_100_businesses_scored.xlsx")

with open(in_csv, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

scored_rows = []
for r in rows:
    score, prob = predict_score(r)
    r_copy = dict(r)
    r_copy["Credit_Score"] = score
    r_copy["Confidence_Pct"] = round(prob * 100, 2)
    r_copy["Decision"] = "Approved" if score >= 50 else "Rejected"
    r_copy["Risk_Tier"] = "Low Risk" if score >= 75 else ("Moderate Risk" if score >= 50 else "High Risk")
    scored_rows.append(r_copy)

fieldnames = list(rows[0].keys()) + ["Credit_Score", "Confidence_Pct", "Decision", "Risk_Tier"]

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(scored_rows)

def col_letter(col_idx):
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result

sheet_rows = []
hdr_cells = [f'<c r="{col_letter(i)}1" t="inlineStr"><is><t>{col}</t></is></c>' for i, col in enumerate(fieldnames, 1)]
sheet_rows.append('<row r="1">' + "".join(hdr_cells) + "</row>")

for r_idx, rec in enumerate(scored_rows, 2):
    row_cells = []
    for c_idx, col in enumerate(fieldnames, 1):
        ref = f"{col_letter(c_idx)}{r_idx}"
        val = str(rec[col])
        if col in ["Decision", "Risk_Tier"]:
            row_cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{val}</t></is></c>')
        else:
            row_cells.append(f'<c r="{ref}"><v>{val}</v></c>')
    sheet_rows.append(f'<row r="{r_idx}">' + "".join(row_cells) + "</row>")

sheet_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">\n'
    '<sheetData>\n' + '\n'.join(sheet_rows) + '\n</sheetData>\n'
    '</worksheet>'
)

content_types_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
    '<Default Extension="xml" ContentType="application/xml"/>\n'
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>\n'
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>\n'
    '</Types>'
)

rels_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n'
    '</Relationships>'
)

workbook_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
    '<sheets>\n'
    '<sheet name="Scored_Businesses" sheetId="1" r:id="rId1"/>\n'
    '</sheets>\n'
    '</workbook>'
)

wb_rels_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\n'
    '</Relationships>'
)

with zipfile.ZipFile(out_xlsx, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types_xml)
    z.writestr("_rels/.rels", rels_xml)
    z.writestr("xl/workbook.xml", workbook_xml)
    z.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
    z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

print(f"Created pre-scored benchmark in {out_xlsx}")
