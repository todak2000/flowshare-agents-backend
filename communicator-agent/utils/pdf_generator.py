"""
PDF Generation for Reconciliation Reports

Converts HTML reconciliation reports to professional PDFs
Uses WeasyPrint for HTML to PDF conversion
"""

import os
import tempfile
from datetime import datetime
from typing import Optional
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


def get_pdf_css() -> str:
    """
    Get CSS styling for PDF generation

    Returns:
        CSS string for PDF styling
    """
    return """
    @page {
        size: A4;
        margin: 2cm 1.5cm;
        @top-center {
            content: "FlowShare Reconciliation Report";
            font-size: 10pt;
            color: #718096;
        }
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 9pt;
            color: #a0aec0;
        }
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #1a202c;
        background-color: #ffffff;
        font-size: 11pt;
    }

    .pdf-header {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 30px;
        border-radius: 8px;
    }

    .pdf-header h1 {
        font-size: 24pt;
        margin-bottom: 10px;
        font-weight: bold;
    }

    .pdf-header .subtitle {
        font-size: 12pt;
        color: #e0e7ff;
    }

    .section {
        margin-bottom: 25px;
        page-break-inside: avoid;
    }

    .section-title {
        font-size: 16pt;
        font-weight: bold;
        color: #2d3748;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 2px solid #667eea;
    }

    .info-box {
        background-color: #f7fafc;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }

    .info-box h3 {
        font-size: 13pt;
        color: #4a5568;
        margin-bottom: 10px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 10px;
    }

    .summary-item {
        padding: 8px 0;
    }

    .summary-label {
        font-weight: 600;
        color: #4a5568;
        font-size: 10pt;
    }

    .summary-value {
        color: #1a202c;
        font-size: 11pt;
        font-weight: 600;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
    }

    thead {
        background-color: #edf2f7;
    }

    th {
        padding: 10px 8px;
        text-align: left;
        font-weight: 600;
        color: #2d3748;
        border-bottom: 2px solid #cbd5e0;
        font-size: 10pt;
    }

    th.right-align {
        text-align: right;
    }

    td {
        padding: 10px 8px;
        border-bottom: 1px solid #e2e8f0;
        color: #4a5568;
    }

    td.right-align {
        text-align: right;
    }

    tr:last-child td {
        border-bottom: none;
    }

    .partner-name {
        font-weight: 600;
        color: #1a202c;
    }

    .positive {
        color: #10b981;
    }

    .negative {
        color: #ef4444;
    }

    .efficiency-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 9pt;
    }

    .efficiency-high {
        background-color: #d1fae5;
        color: #065f46;
    }

    .efficiency-medium {
        background-color: #fef3c7;
        color: #92400e;
    }

    .efficiency-low {
        background-color: #fee2e2;
        color: #991b1b;
    }

    .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
        font-size: 9pt;
        color: #718096;
        text-align: center;
    }

    .ai-summary {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        margin: 20px 0;
        border-radius: 4px;
    }

    .ai-summary h3 {
        color: #1e40af;
        font-size: 12pt;
        margin-bottom: 10px;
    }

    .ai-summary p {
        color: #475569;
        line-height: 1.6;
        margin-bottom: 8px;
    }
    """


def generate_reconciliation_pdf_html(reconciliation_data: dict, ai_summary: str = "") -> str:
    """
    Generate HTML content for PDF reconciliation report

    Args:
        reconciliation_data: Dictionary with reconciliation details
        ai_summary: AI-generated executive summary

    Returns:
        HTML string ready for PDF conversion
    """
    period_start = reconciliation_data.get('period_start', '')
    period_end = reconciliation_data.get('period_end', '')
    period_month = reconciliation_data.get('period_month', '')
    allocations_count = reconciliation_data.get('allocations_count', 0)
    total_input = reconciliation_data.get('total_input_volume', 0)
    terminal_volume = reconciliation_data.get('terminal_volume', 0)
    allocated_volume = reconciliation_data.get('allocated_volume', 0)
    shrinkage = reconciliation_data.get('shrinkage_factor', 0)
    volume_loss = reconciliation_data.get('volume_loss', 0)
    allocations = reconciliation_data.get('allocations', [])

    # Generate allocation table rows
    allocation_rows = ""
    for alloc in allocations:
        partner = alloc.get('partner', 'Unknown')
        input_vol = alloc.get('input_volume', 0)
        allocated_vol = alloc.get('allocated_volume', 0)
        loss = alloc.get('volume_loss', 0)
        pct = alloc.get('percentage', 0)
        efficiency = (allocated_vol / input_vol * 100) if input_vol > 0 else 0

        # Determine efficiency class
        efficiency_class = "efficiency-high" if efficiency >= 95 else "efficiency-medium" if efficiency >= 90 else "efficiency-low"
        loss_class = "negative" if loss > 0 else "positive"

        allocation_rows += f"""
        <tr>
            <td class="partner-name">{partner}</td>
            <td class="right-align">{input_vol:,.2f}</td>
            <td class="right-align positive">{allocated_vol:,.2f}</td>
            <td class="right-align {loss_class}">{abs(loss):,.2f}</td>
            <td class="right-align">{pct:.2f}%</td>
            <td class="right-align"><span class="efficiency-badge {efficiency_class}">{efficiency:.1f}%</span></td>
        </tr>
        """

    # AI Summary section
    ai_section = ""
    if ai_summary:
        ai_section = f"""
        <div class="section">
            <div class="ai-summary">
                <h3>🤖 Executive Summary</h3>
                {ai_summary.replace('\n', '<br>')}
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reconciliation Report - {period_month}</title>
    </head>
    <body>
        <!-- Header -->
        <div class="pdf-header">
            <h1>📊 FlowShare Reconciliation Report</h1>
            <div class="subtitle">{period_month} ({period_start} to {period_end})</div>
        </div>

        {ai_section}

        <!-- Period Information -->
        <div class="section">
            <div class="info-box">
                <h3>📅 Reconciliation Overview</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Period:</div>
                        <div class="summary-value">{period_start} to {period_end}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Partners:</div>
                        <div class="summary-value">{allocations_count}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Input Volume:</div>
                        <div class="summary-value">{total_input:,.2f} BBL</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Terminal Volume:</div>
                        <div class="summary-value">{terminal_volume:,.2f} BBL</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Allocated Volume:</div>
                        <div class="summary-value">{allocated_volume:,.2f} BBL</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Volume Loss/Gain:</div>
                        <div class="summary-value {'negative' if volume_loss > 0 else 'positive'}">{abs(volume_loss):,.2f} BBL</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Shrinkage Factor:</div>
                        <div class="summary-value">{abs(shrinkage):.2f}%</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Generated:</div>
                        <div class="summary-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Partner Allocations -->
        <div class="section">
            <h2 class="section-title">👥 Partner Allocations</h2>
            <table>
                <thead>
                    <tr>
                        <th>Partner</th>
                        <th class="right-align">Input (BBL)</th>
                        <th class="right-align">Allocated (BBL)</th>
                        <th class="right-align">Loss/Gain (BBL)</th>
                        <th class="right-align">Share (%)</th>
                        <th class="right-align">Efficiency</th>
                    </tr>
                </thead>
                <tbody>
                    {allocation_rows}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Note:</strong> This report reflects the proportional back-allocation of terminal volumes
            to each partner based on their net volume contributions for {period_month}.</p>
            <p style="margin-top: 10px;">© {datetime.now().year} FlowShare. All rights reserved.</p>
        </div>
    </body>
    </html>
    """

    return html_content


async def generate_reconciliation_pdf(
    reconciliation_data: dict,
    ai_summary: str = "",
    output_filename: Optional[str] = None
) -> str:
    """
    Generate a PDF file from reconciliation data

    Args:
        reconciliation_data: Dictionary with reconciliation details
        ai_summary: AI-generated executive summary
        output_filename: Optional custom filename (without .pdf extension)

    Returns:
        Path to the generated PDF file
    """
    # Generate HTML content
    html_content = generate_reconciliation_pdf_html(reconciliation_data, ai_summary)

    # Create filename
    if not output_filename:
        period_month = reconciliation_data.get('period_month', 'Unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"reconciliation_{period_month.replace(' ', '_')}_{timestamp}"

    # Create temporary directory for PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f"{output_filename}.pdf")

    # Convert HTML to PDF
    font_config = FontConfiguration()
    html = HTML(string=html_content)
    css = CSS(string=get_pdf_css(), font_config=font_config)

    html.write_pdf(pdf_path, stylesheets=[css], font_config=font_config)

    return pdf_path
