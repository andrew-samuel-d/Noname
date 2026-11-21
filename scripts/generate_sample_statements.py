import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_sharma_kirana_pdf(output_path: str):
    """Generates a realistic HDFC Bank statement for Sharma Kirana Store (Clean, 0 bounces)."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#004b87'))
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#555555'))
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')

    story.append(Paragraph("HDFC BANK LIMITED", title_style))
    story.append(Paragraph("Account Statement • Inward Clearing & Electronic Settlements", sub_style))
    story.append(Spacer(1, 10))

    header_data = [
        ["Account Holder:", "SHARMA KIRANA STORE (PROPRIETOR)", "Account Number:", "XXXX-XXXX-4092"],
        ["Customer ID:", "82910492", "Account Type:", "Current Account — Premium"],
        ["Statement Period:", "01/04/2025 to 31/03/2026", "Branch / IFSC:", "INDORE RAJWAH / HDFC0000123"],
        ["Average Monthly Balance (AMB):", "INR 6,50,000.00", "Total Inward Bounces:", "0 (CLEAN LEDGER)"]
    ]
    t_header = Table(header_data, colWidths=[140, 160, 110, 130])
    t_header.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#222222')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f4f7f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 14))

    story.append(Paragraph("TRANSACTION LEDGER EXTRACT (SAMPLE MONTHLY CYCLE)", bold_style))
    story.append(Spacer(1, 6))

    txn_rows = [
        ["Txn Date", "Narration / Reference Code", "Chq/Ref No", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
        ["02/10/2025", "UPI/PAYTM MERCHANT QR/CR/428192841029", "UPI-428192", "-", "18,450.00", "6,18,450.00"],
        ["05/10/2025", "NEFT INWARD/METRO CASH & CARRY VENDOR", "NEFT-88129", "-", "1,45,000.00", "7,63,450.00"],
        ["08/10/2025", "UPI/PHONEPE BUSINESS QR SETTLEMENT", "UPI-918204", "-", "24,800.00", "7,88,250.00"],
        ["12/10/2025", "CASH DEP CDM MACHINE SELF DEPOSIT", "CDM-0091", "-", "55,000.00", "8,43,250.00"],
        ["15/10/2025", "RTGS INWARD WHOLESALE GRAIN TRADE", "RTGS-40912", "-", "3,20,000.00", "11,63,250.00"],
        ["18/10/2025", "ACH DR / BAJAJ FINSERV LOAN EMI PAID", "ACH-00129", "45,000.00", "-", "11,18,250.00"],
        ["22/10/2025", "UPI/BHARATPE QR MERCH SETTLE", "UPI-339102", "-", "32,600.00", "11,50,850.00"],
        ["26/10/2025", "IMPS/BHIM UPI INWARD PAYMENT", "IMPS-77192", "-", "14,200.00", "11,65,050.00"],
        ["30/10/2025", "MONTHLY CLOSING AMB BALANCE CALC", "SYS-AMB", "-", "-", "6,50,000.00"]
    ]
    t_txns = Table(txn_rows, colWidths=[65, 235, 60, 60, 60, 60])
    t_txns.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004b87')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_txns)
    story.append(Spacer(1, 14))

    summary_text = Paragraph(
        "<b>Summary Analytics:</b> Analyzed 1,420 transactions across 12 months. Total UPI Inflows: ₹50,40,000 | Total Bank Transfers: ₹2,16,00,000 | Statutory Mandate Bounces: 0. Digitally signed via RBI Account Aggregator protocol.",
        sub_style
    )
    story.append(summary_text)

    doc.build(story)


def generate_gupta_trading_pdf(output_path: str):
    """Generates a realistic SBI statement for Gupta General Trading (Stressed, 6 Bounces)."""
    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1b3d6d'))
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#555555'))
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')

    story.append(Paragraph("STATE BANK OF INDIA", title_style))
    story.append(Paragraph("Current Account Statement • Commercial & Institutional Banking", sub_style))
    story.append(Spacer(1, 10))

    header_data = [
        ["Account Holder:", "GUPTA GENERAL TRADING CORP", "Account Number:", "XXXX-XXXX-8911"],
        ["Customer ID:", "19402911", "Account Type:", "Regular Current Account"],
        ["Statement Period:", "01/04/2025 to 31/03/2026", "Branch / IFSC:", "KANPUR MAIN / SBIN0000241"],
        ["Average Monthly Balance (AMB):", "INR 20,000.00", "Total Inward Bounces:", "6 (HIGH RISK BREACH)"]
    ]
    t_header = Table(header_data, colWidths=[140, 160, 110, 130])
    t_header.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#222222')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff5f5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e53e3e')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fed7d7')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 14))

    story.append(Paragraph("TRANSACTION LEDGER EXTRACT (SHOWING BOUNCE INCIDENTS)", bold_style))
    story.append(Spacer(1, 6))

    txn_rows = [
        ["Txn Date", "Narration / Reference Code", "Chq/Ref No", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
        ["14/10/2025", "ACH DR RETURN: HDFC0000123 / INSUFFICIENT BALANCE", "ACH-RET-01", "590.00", "-", "1,240.00"],
        ["02/11/2025", "INWARD CHQ RTN CHG: CTS CLG RET CHQ 004128", "CTS-RET-02", "500.00", "-", "740.00"],
        ["18/12/2025", "NACH MANDATE FAIL: BAJAJ FIN AUTO-DEBIT RET", "ACH-RET-03", "590.00", "-", "150.00"],
        ["05/01/2026", "CHQ DISHONOUR PENALTY: CTS RETURN CLG", "CTS-RET-04", "500.00", "-", "-350.00"],
        ["21/01/2026", "ECS REVERSAL FEE: MIN BALANCE BREACH / RET", "ECS-RET-05", "354.00", "-", "-704.00"],
        ["12/02/2026", "ACH DEBIT RETURN: MUTHOOT FIN EMI RTN", "ACH-RET-06", "590.00", "-", "850.00"],
        ["15/02/2026", "UPI/PAYTM MERCHANT QR INWARD", "UPI-11920", "-", "12,400.00", "13,250.00"],
        ["28/02/2026", "NEFT INWARD/LOCAL SUPPLIER SETTLEMENT", "NEFT-99120", "-", "25,000.00", "38,250.00"]
    ]
    t_txns = Table(txn_rows, colWidths=[65, 235, 60, 60, 60, 60])
    t_txns.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9b2c2c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_txns)
    story.append(Spacer(1, 14))

    summary_text = Paragraph(
        "<b>Auditor Red Flags:</b> 6 Statutory mandate bounces detected (Total Penalty Debits: ₹3,124.00). Inward returns indicate acute short-term cash deficits.",
        sub_style
    )
    story.append(summary_text)

    doc.build(story)


def generate_csv_statements(data_dir: str):
    """Generates matching CSV bank statements for fast spreadsheet testing."""
    # Sharma Kirana (Clean)
    sharma_csv = os.path.join(data_dir, "sample_statement_sharma_kirana.csv")
    with open(sharma_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Narration", "RefNo", "Debit", "Credit", "Balance"])
        writer.writerow(["01-Oct-2025", "HDFC BANK OPENING BALANCE", "OPEN", "", "", "650000.00"])
        writer.writerow(["02-Oct-2025", "UPI/PAYTM QR INWARD CREDIT", "UPI-42819", "", "18450.00", "668450.00"])
        writer.writerow(["05-Oct-2025", "NEFT INWARD METRO CASH CARRY", "NEFT-88129", "", "145000.00", "813450.00"])
        writer.writerow(["08-Oct-2025", "UPI/PHONEPE MERCHANT QR", "UPI-91820", "", "24800.00", "838250.00"])
        writer.writerow(["12-Oct-2025", "CASH DEP CDM MACHINE SELF", "CDM-0091", "", "55000.00", "893250.00"])
        writer.writerow(["15-Oct-2025", "RTGS INWARD WHOLESALE GRAIN", "RTGS-40912", "", "320000.00", "1213250.00"])
        writer.writerow(["18-Oct-2025", "ACH DR / BAJAJ FIN LOAN EMI", "ACH-00129", "45000.00", "", "1168250.00"])
        writer.writerow(["31-Oct-2025", "AMB AVERAGE MONTHLY BALANCE", "SYS-AMB", "", "", "650000.00"])

    # Gupta Trading (6 Bounces)
    gupta_csv = os.path.join(data_dir, "sample_statement_gupta_trading.csv")
    with open(gupta_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Narration", "RefNo", "Debit", "Credit", "Balance"])
        writer.writerow(["01-Oct-2025", "SBI OPENING BALANCE", "OPEN", "", "", "20000.00"])
        writer.writerow(["14-Oct-2025", "ACH DR RETURN: HDFC0000123 / INSUFFICIENT BALANCE", "ACH-RET-01", "590.00", "", "1240.00"])
        writer.writerow(["02-Nov-2025", "INWARD CHQ RTN CHG: CTS CLG RET CHQ 004128", "CTS-RET-02", "500.00", "", "740.00"])
        writer.writerow(["18-Dec-2025", "NACH MANDATE FAIL: BAJAJ FIN AUTO-DEBIT RET", "ACH-RET-03", "590.00", "", "150.00"])
        writer.writerow(["05-Jan-2026", "CHQ DISHONOUR PENALTY: CTS RETURN CLG", "CTS-RET-04", "500.00", "", "-350.00"])
        writer.writerow(["21-Jan-2026", "ECS REVERSAL FEE: MIN BALANCE BREACH / RET", "ECS-RET-05", "354.00", "", "-704.00"])
        writer.writerow(["12-Feb-2026", "ACH DEBIT RETURN: MUTHOOT FIN EMI RTN", "ACH-RET-06", "590.00", "", "850.00"])
        writer.writerow(["15-Feb-2026", "UPI/PAYTM MERCHANT QR INWARD", "UPI-11920", "", "12400.00", "13250.00"])
        writer.writerow(["31-Mar-2026", "AMB AVERAGE MONTHLY BALANCE", "SYS-AMB", "", "", "20000.00"])


if __name__ == "__main__":
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(d, exist_ok=True)
    generate_sharma_kirana_pdf(os.path.join(d, "sample_statement_sharma_kirana.pdf"))
    generate_gupta_trading_pdf(os.path.join(d, "sample_statement_gupta_trading.pdf"))
    generate_csv_statements(d)
    print("✅ Sample PDF and CSV bank statements generated in data/ folder!")
