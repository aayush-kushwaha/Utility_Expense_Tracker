from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
from datetime import datetime

def generate_expense_report(data: pd.DataFrame, filename: str = "expense_report.pdf"):
    """Generate a PDF report of electricity and rent expenses."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Utility Expense Report", title_style))
    story.append(Spacer(1, 12))

    # Generate date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=30
    )
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
    story.append(Spacer(1, 12))

    # Summary Statistics
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    story.append(Paragraph("Summary Statistics", summary_style))
    
    total_electricity = data['electricity_cost'].sum()
    total_rent = data['rent'].sum()
    total_cost = data['total_cost'].sum()
    avg_consumption = data['consumption'].mean()

    summary_data = [
        ["Total Electricity Cost:", f"₹{total_electricity:,.2f}"],
        ["Total Rent:", f"₹{total_rent:,.2f}"],
        ["Total Expenses:", f"₹{total_cost:,.2f}"],
        ["Average Monthly Consumption:", f"{avg_consumption:.1f} units"]
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Monthly Details
    story.append(Paragraph("Monthly Details", summary_style))
    
    # Prepare data for the detailed table
    detailed_data = [['Month', 'Consumption (units)', 'Electricity Cost', 'Rent', 'Total']]
    for _, row in data.iterrows():
        detailed_data.append([
            row['month'],
            f"{row['consumption']:.1f}",
            f"₹{row['electricity_cost']:,.2f}",
            f"₹{row['rent']:,.2f}",
            f"₹{row['total_cost']:,.2f}"
        ])

    # Create the detailed table
    detailed_table = Table(detailed_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.4*inch, 1.4*inch])
    detailed_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
    ]))

    story.append(detailed_table)
    
    # Build the PDF
    doc.build(story)
    return filename
