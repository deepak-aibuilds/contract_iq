from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

contract_text = """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024,
by and between Hargrove & Finch LLP ("Client") and TechCorp Inc ("Provider").

1. PAYMENT TERMS
Client agrees to pay Provider $5,000 per month, due on the first of each month.
Late payments incur a 1.5% monthly penalty after 15 days.

2. TERMINATION
Either party may terminate this Agreement with 30 days written notice.
Termination for cause requires written notice and a 10-day cure period.

3. AUTO-RENEWAL
This Agreement renews automatically for successive one-year terms unless
either party provides 60 days written notice prior to expiration.

4. GOVERNING LAW
This Agreement shall be governed by the laws of the State of New York.

5. LIABILITY
Provider liability is capped at the total fees paid in the prior 3 months.
"""

for line in contract_text.split('\n'):
    pdf.cell(200, 10, txt=line, ln=True)

pdf.output("test_contract.pdf")
print("Done")