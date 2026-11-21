import os
import csv
import zipfile
import random

random.seed(42)

FEATURE_ORDER = [
    "business_age_years",
    "monthly_upi_volume",
    "monthly_bank_volume",
    "monthly_cash_volume",
    "gst_filing_regularity",
    "gst_turnover",
    "bounce_frequency",
    "avg_monthly_balance",
    "income_stability",
    "seasonality_score",
    "loan_default_history"
]

records = []

# 1-35: Prime / Low Risk businesses (High liquidity, 0 bounce, clean history)
for _ in range(35):
    records.append({
        "business_age_years": random.randint(5, 20),
        "monthly_upi_volume": random.randint(250000, 1000000),
        "monthly_bank_volume": random.randint(1500000, 5000000),
        "monthly_cash_volume": random.randint(40000, 200000),
        "gst_filing_regularity": random.randint(90, 100),
        "gst_turnover": random.randint(15000000, 50000000),
        "bounce_frequency": 0,
        "avg_monthly_balance": random.randint(450000, 2000000),
        "income_stability": random.randint(80, 98),
        "seasonality_score": random.randint(65, 95),
        "loan_default_history": 0
    })

# 36-70: Moderate / Mid Risk businesses (Standard profiles, 0-2 bounces)
for _ in range(35):
    records.append({
        "business_age_years": random.randint(3, 10),
        "monthly_upi_volume": random.randint(100000, 400000),
        "monthly_bank_volume": random.randint(500000, 2000000),
        "monthly_cash_volume": random.randint(20000, 150000),
        "gst_filing_regularity": random.randint(75, 92),
        "gst_turnover": random.randint(5000000, 20000000),
        "bounce_frequency": random.choice([0, 1, 2]),
        "avg_monthly_balance": random.randint(150000, 500000),
        "income_stability": random.randint(60, 82),
        "seasonality_score": random.randint(45, 75),
        "loan_default_history": 0
    })

# 71-100: Stressed / High Risk businesses (Low balance, multiple bounces, defaults)
for _ in range(30):
    records.append({
        "business_age_years": random.randint(1, 4),
        "monthly_upi_volume": random.randint(20000, 150000),
        "monthly_bank_volume": random.randint(80000, 600000),
        "monthly_cash_volume": random.randint(10000, 80000),
        "gst_filing_regularity": random.randint(50, 75),
        "gst_turnover": random.randint(500000, 5000000),
        "bounce_frequency": random.randint(3, 10),
        "avg_monthly_balance": random.randint(10000, 90000),
        "income_stability": random.randint(35, 60),
        "seasonality_score": random.randint(30, 55),
        "loan_default_history": random.choice([0, 1, 1])
    })

# Shuffle to simulate mixed real-world batches
random.shuffle(records)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# 1. Save CSV
csv_path = os.path.join(data_dir, "sample_100_businesses_input.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FEATURE_ORDER)
    writer.writeheader()
    writer.writerows(records)

# 2. Build OpenXML .xlsx file directly
xlsx_path = os.path.join(data_dir, "sample_100_businesses_input.xlsx")

def col_letter(col_idx):
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result

sheet_rows = []

# Header row
hdr_cells = []
for c_idx, col in enumerate(FEATURE_ORDER, 1):
    ref = f"{col_letter(c_idx)}1"
    hdr_cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{col}</t></is></c>')
sheet_rows.append(f'<row r="1">' + "".join(hdr_cells) + "</row>")

# Data rows
for r_idx, rec in enumerate(records, 2):
    row_cells = []
    for c_idx, col in enumerate(FEATURE_ORDER, 1):
        ref = f"{col_letter(c_idx)}{r_idx}"
        val = rec[col]
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
    '<sheet name="Businesses" sheetId="1" r:id="rId1"/>\n'
    '</sheets>\n'
    '</workbook>'
)

wb_rels_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>\n'
    '</Relationships>'
)

with zipfile.ZipFile(xlsx_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types_xml)
    z.writestr("_rels/.rels", rels_xml)
    z.writestr("xl/workbook.xml", workbook_xml)
    z.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
    z.writestr("xl/worksheets/sheet1.xml", sheet_xml)

print(f"Created {len(records)} sample businesses in:")
print(f"   - Excel: {xlsx_path}")
print(f"   - CSV:   {csv_path}")
