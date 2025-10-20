"""
Professional Email Templates for FlowShare
Updated with new header/footer design
"""
import os
import datetime


def get_email_template(body_content: str, preheader: str = "", show_header_right: bool = False, 
                       report_type: str = "", date_range: str = "") -> str:
    """
    Generate a professional HTML email with FlowShare branding
    
    Args:
        body_content: Main content of the email (HTML string)
        preheader: Short preview text shown in email clients
        show_header_right: Whether to show the right side of header (for PDF reports)
        report_type: Text for report type (only if show_header_right is True)
        date_range: Date range text (only if show_header_right is True)
    
    Returns:
        Fully formatted HTML email with FlowShare branding
    """
    current_year = datetime.datetime.now().year

    # Conditional header right section
    header_right_html = ""
    header_title=preheader
    if show_header_right:
        header_title="Reconciliation Report"
        header_right_html = f"""
        <!-- Right side: Report Type and Date -->
        <div class="header-right">
          <div class="report-type">{report_type or 'Production Allocation'}</div>
          <div class="date">{date_range}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FlowShare Notification</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.5;
      color: #1f2937;
      background-color: #f5f5f5;
      padding: 20px;
    }}

    .email-container {{
      max-width: 650px;
      margin: 20px auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    .header {{
      background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
      padding: 40px 30px;
      margin: 0;
      color: white;
      position: relative;
      overflow: hidden;
      width: 100%;
      box-sizing: border-box;
    }}

    .header::before {{
      content: '';
      position: absolute;
      top: -50%;
      right: -10%;
      width: 300px;
      height: 300px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50%;
    }}

    .header-content {{
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      max-width: 100%;
      flex-wrap: wrap;
      gap: 20px;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 20px;
    }}

    .logo-img {{
      width: 100px;
      height: 100px;
      background: transparent;
      border-radius: 12px;
      padding: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}

    .header-text {{
      text-align: left;
    }}

    .company-name {{
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 5px;
      letter-spacing: -0.5px;
    }}

    .period {{
      font-size: 16px;
      opacity: 0.9;
      font-weight: 500;
    }}

    .header-right {{
      text-align: right;
    }}

    .report-type {{
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
      opacity: 0.8;
      margin-bottom: 5px;
      font-weight: 600;
    }}

    .date {{
      font-size: 13px;
      opacity: 0.9;
    }}

    .content {{
      padding: 40px 35px;
    }}

    .content h1 {{
      color: #1e293b;
      font-size: 24px;
      margin-bottom: 10px;
    }}

    .content h2 {{
      color: #1e293b;
      font-size: 18px;
      margin: 30px 0 15px 0;
    }}

    .content p {{
      color: #475569;
      margin-bottom: 20px;
      font-size: 15px;
    }}

    .info-section {{
      background-color: #f8fafc;
      border-radius: 8px;
      padding: 20px;
      margin: 25px 0;
    }}

    .info-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #e2e8f0;
    }}

    .info-row:last-child {{
      border-bottom: none;
    }}

    .info-label {{
      color: #64748b;
      font-size: 14px;
    }}

    .info-value {{
      color: #1e293b;
      font-weight: 600;
      font-size: 14px;
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 25px 0;
      font-size: 14px;
    }}

    .data-table thead {{
      background-color: #1e293b;
      color: white;
    }}

    .data-table th {{
      padding: 14px 12px;
      text-align: left;
      font-weight: 600;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}

    .data-table th.right {{
      text-align: right;
    }}

    .data-table td {{
      padding: 14px 12px;
      border-bottom: 1px solid #e2e8f0;
      color: #334155;
    }}

    .data-table td.right {{
      text-align: right;
    }}

    .data-table tbody tr:hover {{
      background-color: #f8fafc;
    }}

    .data-table tbody tr:last-child td {{
      border-bottom: none;
    }}

    .partner-name {{
      font-weight: 600;
      color: #1e293b;
    }}

    .positive {{
      color: #10b981;
      font-weight: 500;
    }}

    .negative {{
      color: #ef4444;
      font-weight: 500;
    }}

    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }}

    .badge-green {{
      background-color: #d1fae5;
      color: #065f46;
    }}

    .badge-yellow {{
      background-color: #fef3c7;
      color: #92400e;
    }}

    .ai-summary {{
      background-color: #eff6ff;
      border-left: 4px solid #3b82f6;
      padding: 20px;
      margin: 25px 0;
      border-radius: 4px;
    }}

    .ai-summary h3 {{
      color: #1e40af;
      font-size: 16px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
    }}

    .ai-summary p {{
      color: #1e293b;
      margin-bottom: 10px;
      line-height: 1.6;
    }}

    .footer {{
      background-color: #f8fafc;
      padding: 25px 35px;
      text-align: center;
      border-top: 1px solid #e2e8f0;
    }}

    .footer p {{
      color: #64748b;
      font-size: 13px;
      margin: 5px 0;
    }}

    @media only screen and (max-width: 600px) {{
      .email-container {{
        margin: 10px;
      }}
      
      .content {{
        padding: 25px 20px;
      }}

      .header {{
        padding: 25px 20px;
      }}

      .header-content {{
        flex-direction: column;
        text-align: center;
      }}

      .header-left {{
        flex-direction: column;
      }}

      .header-text {{
        text-align: center;
      }}

      .header-right {{
        text-align: center;
      }}

      .company-name {{
        font-size: 24px;
      }}

      .data-table {{
        font-size: 12px;
      }}

      .data-table th,
      .data-table td {{
        padding: 10px 8px;
      }}
    }}
  </style>
</head>
<body>
  <div style="display: none; max-height: 0px; overflow: hidden;">
    {preheader}
  </div>

  <div class="email-container">
    <!-- Header Section -->
    <div class="header">
      <div class="header-content">
        <!-- Left side: Logo and Company Info -->
        <div class="header-left">
          <div class="logo-img">
            <img src="https://firebasestorage.googleapis.com/v0/b/back-allocation.firebasestorage.app/o/logo.webp?alt=media&token=a14f4e59-df8d-41bd-ae0c-3a1224c86033" 
                 style="width: 100%; height: 100%; object-fit: contain;" 
                 alt="FlowShare Logo"/>
          </div>
          <div class="header-text">
            <div class="company-name">FlowShare</div>
            <div class="period">{header_title}</div>
          </div>
        </div>

        {header_right_html}
      </div>
    </div>

    <div class="content">
      {body_content}
    </div>

    <div class="footer">
      <p><strong>FlowShare</strong> - Automated Production Allocation Platform</p>
      <p>© {current_year} FlowShare. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""


def format_ai_reconciliation_report(reconciliation_data: dict, ai_summary: str = "") -> str:
    """
    Format comprehensive reconciliation report with clean table layout
    
    Args:
        reconciliation_data: Dictionary with reconciliation details
        ai_summary: AI-generated executive summary (optional)
    
    Returns:
        HTML formatted email body with full report
    """
    period_start = reconciliation_data.get('period_start', '')
    period_end = reconciliation_data.get('period_end', '')
    period_month = reconciliation_data.get('period_month', '')
    allocations_count = reconciliation_data.get('allocations_count', 0)
    total_input = reconciliation_data.get('total_input_volume', 0)
    terminal_volume = reconciliation_data.get('terminal_volume', 0)
    shrinkage = reconciliation_data.get('shrinkage_factor', 0)
    volume_loss = reconciliation_data.get('volume_loss', 0)
    allocated_volume = reconciliation_data.get('allocated_volume', terminal_volume)
    allocations = reconciliation_data.get('allocations', [])

    # Generate allocation table rows
    allocation_rows = ""
    for alloc in allocations:
        partner = alloc.get('partner', 'Unknown')
        input_vol = alloc.get('input_volume', 0)
        allocated_vol = alloc.get('allocated_volume', 0)
        loss = alloc.get('volume_loss', 0)
        share_pct = alloc.get('percentage', 0)
        efficiency = alloc.get('efficiency', 0)
        
        if efficiency == 0 and input_vol > 0:
            efficiency = (allocated_vol / input_vol * 100)

        # Determine badge color based on efficiency
        badge_class = 'badge-green' if efficiency >= 96 else 'badge-yellow'
        loss_class = 'negative' if loss > 0 else 'positive'

        allocation_rows += f"""
            <tr>
                <td><span class="partner-name">{partner}</span></td>
                <td class="right">{input_vol:,.0f} bbl</td>
                <td class="right positive">{allocated_vol:,.2f} bbl</td>
                <td class="right {loss_class}">{loss:,.2f} bbl</td>
                <td class="right">{share_pct:.2f}%</td>
                <td class="right"><span class="badge {badge_class}">{efficiency:.1f}%</span></td>
            </tr>
        """

    body = f"""
        <h1>Reconciliation Report - {period_start} - {period_end}</h1>
        
        <div class="info-section">
            <div class="info-row">
                <span class="info-label">Period:</span>
                <span class="info-value">{period_start} - {period_end}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Run Date:</span>
                <span class="info-value">{reconciliation_data.get('run_date', 'N/A')}</span>
            </div>
        </div>

        <h2>📊 Volume Summary</h2>
        
        <div class="info-section">
            <div class="info-row">
                <span class="info-label">Total Partners:</span>
                <span class="info-value">{allocations_count}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Input Volume:</span>
                <span class="info-value">{total_input:,.0f} BBL</span>
            </div>
            <div class="info-row">
                <span class="info-label">Terminal Volume:</span>
                <span class="info-value">{terminal_volume:,.0f} BBL</span>
            </div>
            <div class="info-row">
                <span class="info-label">Volume Loss/Gain:</span>
                <span class="info-value" style="color: #ef4444;">{volume_loss:,.0f} BBL</span>
            </div>
            <div class="info-row">
                <span class="info-label">Shrinkage:</span>
                <span class="info-value" style="color: #f59e0b;">{abs(shrinkage):.2f}%</span>
            </div>
            <div class="info-row">
                <span class="info-label">Allocated Volume:</span>
                <span class="info-value" style="color: #10b981;">{allocated_volume:,.0f} BBL</span>
            </div>
        </div>

        <h2>👥 Partner Allocations</h2>
        
        <table class="data-table">
            <thead>
                <tr>
                    <th>PARTNER</th>
                    <th class="right">INPUT VOL</th>
                    <th class="right">ALLOCATED VOL</th>
                    <th class="right">GAIN/LOSS</th>
                    <th class="right">SHARE</th>
                    <th class="right">EFFICIENCY</th>
                </tr>
            </thead>
            <tbody>
                {allocation_rows}
            </tbody>
        </table>

        {f'''
        <div class="ai-summary">
            <h3>🤖 AI Analysis</h3>
            {format_markdown_for_email(ai_summary)}
        </div>
        ''' if ai_summary else ''}

        <p style="color: #64748b; font-size: 13px; margin-top: 30px;">
            This report reflects the proportional back-allocation of terminal volumes to each partner 
            based on their net volume contributions for {period_month}.
        </p>
    """

    return get_email_template(
        body, 
        f"Reconciliation Report - {period_month}",
        show_header_right=True,
        report_type="Production Allocation",
        date_range=f"{period_start} - {period_end}"
    )


def format_markdown_for_email(text: str) -> str:
    """
    Convert Markdown-like text to HTML for email display

    Args:
        text: Text with markdown formatting

    Returns:
        HTML formatted text
    """
    import re

    # Remove markdown code blocks
    text = re.sub(r'```(?:html|xml|css|javascript|js)?\s*\n?', '', text)
    text = re.sub(r'```\s*$', '', text)

    # Convert bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    # Convert headers
    text = re.sub(r'^##\s+(.+)$', r'<h4 style="color: #1e293b; margin-top: 15px; margin-bottom: 8px; font-size: 15px;">\1</h4>', text, flags=re.MULTILINE)

    # Convert bullet points
    lines = text.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul style="margin: 10px 0; padding-left: 20px;">')
                in_list = True
            item_text = stripped[2:]
            formatted_lines.append(f'<li style="margin-bottom: 6px; color: #334155;">{item_text}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if stripped:
                formatted_lines.append(f'<p style="margin-bottom: 10px; color: #334155;">{stripped}</p>')

    if in_list:
        formatted_lines.append('</ul>')

    return '\n'.join(formatted_lines)


def format_reconciliation_pdf_email(reconciliation_data: dict, pdf_download_url: str) -> str:
    """
    Format reconciliation email with PDF download link
    
    Args:
        reconciliation_data: Dictionary with reconciliation details
        pdf_download_url: URL to download the PDF report
    
    Returns:
        HTML formatted email body with download link
    """
    period_month = reconciliation_data.get('period_month', '')
    period_start = reconciliation_data.get('period_start', '')
    period_end = reconciliation_data.get('period_end', '')

    body = f"""
        <h1>📊 {period_month} Reconciliation Report Ready</h1>
        
        <p>Your detailed reconciliation report for <strong>{period_start} to {period_end}</strong> is now available.</p>

        <div style="text-align: center; margin: 35px 0;">
            <a href="{pdf_download_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 15px;">
                📥 Download PDF Report
            </a>
        </div>

        <p style="color: #64748b; font-size: 13px;">
            The PDF includes detailed partner allocations, AI-powered insights, and comprehensive volume analysis. 
            This link will be available for 7 days.
        </p>
    """

    return get_email_template(body, f"{period_month} Reconciliation Report Ready")


def format_reconciliation_login_notification(reconciliation_data: dict, login_url: str = None) -> str:
    """
    Format reconciliation notification email directing users to log in

    Args:
        reconciliation_data: Dictionary with reconciliation details
        login_url: Optional URL to the login page (defaults to reconciliation page)

    Returns:
        HTML formatted email body prompting login
    """
    period_month = reconciliation_data.get('period_month', '')
    period_start = reconciliation_data.get('period_start', '')
    period_end = reconciliation_data.get('period_end', '')

    # Default to reconciliation page
    if not login_url:
        frontend_url = os.getenv('FRONTEND_URL', 'https://flowshare-197665497260.europe-west1.run.app')
        login_url = f"{frontend_url}/onboarding/login"

    body = f"""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 6px;">
            <p style="margin: 0; color: #1e40af; font-size: 14px;">
                <strong>🔐 Secure Access Required</strong><br>
                To view your reconciliation report, AI-powered insights, and detailed partner allocations, please log in to your FlowShare account.
            </p>
        </div>

        <div style="text-align: center; margin: 35px 0;">
            <a href="{login_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 15px;">
                🚀 View Report in FlowShare
            </a>
        </div>

        <p style="color: #64748b; font-size: 13px;">
            All reports are securely stored in your FlowShare account and accessible anytime.
            If you have any questions, please contact your JV coordinator.
        </p>
    """

    return get_email_template(body, f"{period_month} Reconciliation Report Ready")


def format_generic_notification(title: str, message: str, action_url: str = "", action_text: str = "Take Action") -> str:
    """
    Format a generic notification email with FlowShare branding.

    Args:
        title: The main heading and title of the email.
        message: The body content of the email. Supports basic markdown.
        action_url: An optional URL for a call-to-action button.
        action_text: The text for the action button (e.g., "View Details").

    Returns:
        A fully formatted HTML email string.
    """
    action_button_html = ""
    if action_url:
        action_button_html = f"""
            <div style="text-align: center; margin: 35px 0;">
                <a href="{action_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 15px;">
                    {action_text}
                </a>
            </div>
        """

    formatted_message = format_markdown_for_email(message)

    body_content = f"""
        <h1>{title}</h1>
        
        {formatted_message}
        
        {action_button_html}
        
        <p style="color: #64748b; font-size: 13px; margin-top: 30px;">
            This is an automated notification from the FlowShare system. If you believe you received this in error, please disregard this email.
        </p>
    """

    return get_email_template(body_content, preheader=title)