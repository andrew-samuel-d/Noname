import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf_statement(filename, bank_name, borrower_name, acc_no, ifsc, amb_str, bounces_count, txns, theme_color, is_clean):
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    c_primary = colors.HexColor(theme_color)
    c_dark = colors.HexColor('#1a202c')
    c_muted = colors.HexColor('#4a5568')

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=c_primary, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=c_muted)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold', textColor=c_dark)
    badge_style = ParagraphStyle('Badge', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#065f46') if is_clean else colors.HexColor('#991b1b'))

    # Header
    story.append(Paragraph(bank_name.upper(), title_style))
    story.append(Paragraph("OFFICIAL COMMERCIAL BANK STATEMENT • RBI ACCOUNT AGGREGATOR CONSENT ARTIFACT", sub_style))
    story.append(Spacer(1, 10))

    # Meta Table
    meta_data = [
        ["Account Holder:", borrower_name, "Account Number:", acc_no],
        ["Customer ID / CIF:", "774910294", "Account Type:", "Current Account (CA-SME)"],
        ["Statement Period:", "01/04/2025 to 31/03/2026 (12M)", "Branch / IFSC:", ifsc],
        ["Average Monthly Balance (AMB):", f"INR {amb_str}", "Total Inward Bounces:", f"{bounces_count} ({'CLEAN REPAYMENT' if bounces_count == 0 else 'HIGH RISK BREACH'})"],
        ["Digital Consent ID:", "AA-CONSENT-99410-SHM", "Verification Protocol:", "Sahamati FIP Node v2.1.0"]
    ]
    t_meta = Table(meta_data, colWidths=[140, 160, 110, 130])
    t_meta.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), c_dark),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # Transaction Section
    story.append(Paragraph("TRANSACTION LEDGER EXTRACT (SAMPLE RECONCILIATION AUDIT CYCLE)", bold_style))
    story.append(Spacer(1, 6))

    t_txns = Table(txns, colWidths=[65, 235, 60, 60, 60, 60])
    t_txns.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_txns)
    story.append(Spacer(1, 12))

    # Summary Box
    summary_html = f"""
    <b>Automated Bank Statement Analyzer (BSA) Reconciliation:</b><br/>
    • Ingestion Protocol: RBI Account Aggregator Encrypted Payload (SHA-256 Digitally Signed by {bank_name}).<br/>
    • Total Mandate / Cheque Dishonours Detected: <b>{bounces_count} incidents</b>.<br/>
    • Certified Working Capital Liquidity (AMB): <b>INR {amb_str}</b>.<br/>
    • Electronic Inflow Ratio (UPI / POS / NEFT): <b>94.2%</b> of total business turnover.
    """
    story.append(Table([[Paragraph(summary_html, sub_style)]], colWidths=[540], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecfdf5') if is_clean else colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#10b981') if is_clean else colors.HexColor('#ef4444')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    doc.build(story)
    print(f"Generated: {filename}")


def generate_all():
    target_dirs = [
        r"C:\Users\andre\Downloads",
        r"C:\Users\andre\Downloads\CashFlowScore-ML 2"
    ]

    sharma_txns = [
        ["Txn Date", "Narration / Reference Code", "Chq/Ref No", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
        ["02/10/2025", "UPI/PAYTM MERCHANT QR/CR/428192841029", "UPI-428192", "-", "18,450.00", "6,68,450.00"],
        ["05/10/2025", "NEFT INWARD/METRO CASH & CARRY VENDOR", "NEFT-88129", "-", "1,45,000.00", "8,13,450.00"],
        ["08/10/2025", "UPI/PHONEPE BUSINESS QR SETTLEMENT", "UPI-918204", "-", "24,800.00", "8,38,250.00"],
        ["12/10/2025", "CASH DEP CDM MACHINE INDORE SELF", "CDM-0091", "-", "55,000.00", "8,93,250.00"],
        ["15/10/2025", "RTGS INWARD WHOLESALE GRAIN TRADE", "RTGS-40912", "-", "3,20,000.00", "12,13,250.00"],
        ["18/10/2025", "ACH DR / BAJAJ FINSERV LOAN EMI PAID", "ACH-00129", "45,000.00", "-", "11,68,250.00"],
        ["22/10/2025", "UPI/BHARATPE QR DAILY SETTLEMENT", "UPI-339102", "-", "32,600.00", "12,00,850.00"],
        ["26/10/2025", "IMPS/BHIM UPI INWARD RETAIL SALES", "IMPS-77192", "-", "14,200.00", "12,15,050.00"],
        ["28/10/2025", "NEFT OUTWARD/ITC GRAIN DISTRIBUTOR", "NEFT-11029", "1,85,000.00", "-", "10,30,050.00"],
        ["31/10/2025", "MONTHLY CLOSING AMB BALANCE CALC", "SYS-AMB", "-", "-", "6,50,000.00"]
    ]

    gupta_txns = [
        ["Txn Date", "Narration / Reference Code", "Chq/Ref No", "Debit (INR)", "Credit (INR)", "Balance (INR)"],
        ["14/10/2025", "ACH DR RETURN: HDFC0000123 / INSUFFICIENT BALANCE", "ACH-RET-01", "590.00", "-", "1,240.00"],
        ["02/11/2025", "INWARD CHQ RTN CHG: CTS CLG RET CHQ 004128", "CTS-RET-02", "500.00", "-", "740.00"],
        ["18/12/2025", "NACH MANDATE FAIL: BAJAJ FIN AUTO-DEBIT RET", "ACH-RET-03", "590.00", "-", "150.00"],
        ["05/01/2026", "CHQ DISHONOUR PENALTY: CTS RETURN CLG", "CTS-RET-04", "500.00", "-", "-350.00"],
        ["21/01/2026", "ECS REVERSAL FEE: MIN BALANCE BREACH / RET", "ECS-RET-05", "354.00", "-", "-704.00"],
        ["12/02/2026", "ACH DEBIT RETURN: MUTHOOT FIN EMI RTN", "ACH-RET-06", "590.00", "-", "850.00"],
        ["15/02/2026", "UPI/PAYTM MERCHANT QR INWARD", "UPI-11920", "-", "12,400.00", "13,250.00"],
        ["28/02/2026", "NEFT INWARD/LOCAL SUPPLIER SETTLEMENT", "NEFT-99120", "-", "25,000.00", "38,250.00"],
        ["31/03/2026", "AMB AVERAGE MONTHLY BALANCE", "SYS-AMB", "-", "-", "20,000.00"]
    ]

    for d in target_dirs:
        os.makedirs(d, exist_ok=True)
        # Prime Approved Statement (HDFC)
        f_clean = os.path.join(d, "Bank_Statement_Sharma_Kirana_HDFC.pdf")
        build_pdf_statement(f_clean, "HDFC Bank Limited", "SHARMA KIRANA STORE (PROPRIETOR)", "XXXX-XXXX-4092", "INDORE RAJWAH / HDFC0000123", "6,50,000.00", 0, sharma_txns, "#004b87", True)

        # Distressed Rejected Statement (SBI)
        f_stressed = os.path.join(d, "Bank_Statement_Gupta_Trading_SBI.pdf")
        build_pdf_statement(f_stressed, "State Bank of India", "GUPTA GENERAL TRADING CORP", "XXXX-XXXX-8911", "KANPUR MAIN / SBIN0000241", "20,000.00", 6, gupta_txns, "#1e3a8a", False)

if __name__ == "__main__":
    generate_all()
