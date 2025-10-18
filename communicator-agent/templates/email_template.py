"""
Professional Email Templates for FlowShare
Includes branded templates with logo and consistent formatting
"""


def get_email_template(body_content: str, preheader: str = "") -> str:
    """
    Generate a professional HTML email with FlowShare branding

    Args:
        body_content: Main content of the email (HTML string)
        preheader: Short preview text shown in email clients

    Returns:
        Fully formatted HTML email with FlowShare branding
    """
    import datetime
    current_year = datetime.datetime.now().year

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="x-apple-disable-message-reformatting">
    <title>FlowShare Notification</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f4f4f4;
        }}

        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            text-align: center;
        }}

        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
            text-decoration: none;
            letter-spacing: 1px;
        }}

        .logo-subtitle {{
            color: #e0e7ff;
            font-size: 14px;
            margin-top: 8px;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .content h1 {{
            color: #1a202c;
            font-size: 24px;
            margin-bottom: 20px;
        }}

        .content h2 {{
            color: #2d3748;
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        .content h3 {{
            color: #4a5568;
            font-size: 18px;
            margin-top: 25px;
            margin-bottom: 12px;
        }}

        .content p {{
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 16px;
        }}

        .content ul {{
            margin-bottom: 20px;
            padding-left: 20px;
        }}

        .content li {{
            color: #4a5568;
            margin-bottom: 10px;
        }}

        .button {{
            display: inline-block;
            padding: 14px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin: 20px 0;
            text-align: center;
        }}

        .button:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #6940a3 100%);
        }}

        .highlight-box {{
            background-color: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .data-table th {{
            background-color: #edf2f7;
            color: #2d3748;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #cbd5e0;
        }}

        .data-table td {{
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            color: #4a5568;
        }}

        .data-table tr:last-child td {{
            border-bottom: none;
        }}

        .footer {{
            background-color: #2d3748;
            color: #a0aec0;
            padding: 30px;
            text-align: center;
            font-size: 14px;
        }}

        .footer-logo {{
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
        }}

        .footer-links {{
            margin: 20px 0;
        }}

        .footer-link {{
            color: #a0aec0;
            text-decoration: none;
            margin: 0 15px;
        }}

        .footer-link:hover {{
            color: #ffffff;
        }}

        .divider {{
            height: 1px;
            background-color: #e2e8f0;
            margin: 30px 0;
        }}

        @media only screen and (max-width: 600px) {{
            .content {{
                padding: 30px 20px;
            }}

            .header {{
                padding: 30px 20px;
            }}

            .logo {{
                font-size: 28px;
            }}

            .content h1 {{
                font-size: 22px;
            }}

            .button {{
                display: block;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <!-- Preheader Text -->
    <div style="display: none; max-height: 0px; overflow: hidden;">
        {preheader}
    </div>

    <!-- Email Container -->
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center" style="padding: 20px 0; background-color: #f4f4f4;">
                <div class="email-container">

                    <!-- Header -->
                    <div class="header">
                        <div class="logo">
                            ⚡ FLOWSHARE
                        </div>
                        <div class="logo-subtitle">
                            Joint Venture Production Allocation Platform
                        </div>
                    </div>

                    <!-- Content -->
                    <div class="content">
                        {body_content}
                    </div>

                    <!-- Footer -->
                    <div class="footer">
                        <div class="footer-logo">
                            ⚡ FLOWSHARE
                        </div>
                        <p style="margin: 15px 0;">
                            Automated production allocation and reconciliation for joint ventures
                        </p>
                        <div class="footer-links">
                            <a href="#" class="footer-link">Dashboard</a>
                            <a href="#" class="footer-link">Documentation</a>
                            <a href="#" class="footer-link">Support</a>
                        </div>
                        <div style="margin-top: 25px; padding-top: 25px; border-top: 1px solid #4a5568;">
                            <p style="font-size: 12px; color: #718096;">
                                © {current_year} FlowShare. All rights reserved.<br>
                                This is an automated message from the FlowShare system.
                            </p>
                        </div>
                    </div>

                </div>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def format_ai_reconciliation_report(reconciliation_data: dict, ai_summary: str = "") -> str:
    """
    Format comprehensive reconciliation report with AI summary

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

        allocation_rows += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;"><strong>{partner}</strong></td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right;">{input_vol:,.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #10b981;">{allocated_vol:,.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right; color: {'#ef4444' if loss > 0 else '#10b981'};">{loss:,.2f}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right;">{pct:.2f}%</td>
                    <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right;">{efficiency:.1f}%</td>
                </tr>
        """

    body = f"""
        <h1>📊 {period_month} Reconciliation Report</h1>

        <p>Hello,</p>

        <p>The reconciliation for <strong>{period_month}</strong> ({period_start} to {period_end}) has been completed successfully.</p>

        {f'<div class="highlight-box"><h3>🤖 Executive Summary</h3>{ai_summary}</div>' if ai_summary else ''}

        <div class="highlight-box">
            <h3>📈 Reconciliation Overview</h3>
            <table class="data-table" style="width: 100%; margin-top: 15px;">
                <tr>
                    <td><strong>Period:</strong></td>
                    <td>{period_start} to {period_end}</td>
                    <td><strong>Total Partners:</strong></td>
                    <td>{allocations_count}</td>
                </tr>
                <tr>
                    <td><strong>Total Input Volume:</strong></td>
                    <td>{total_input:,.2f} BBL</td>
                    <td><strong>Terminal Volume:</strong></td>
                    <td>{terminal_volume:,.2f} BBL</td>
                </tr>
                <tr>
                    <td><strong>Shrinkage Factor:</strong></td>
                    <td colspan="3">{abs(shrinkage):.2f}%</td>
                </tr>
            </table>
        </div>

        <h2>👥 Partner Allocations</h2>
        <table class="data-table" style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead style="background-color: #edf2f7;">
                <tr>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #cbd5e0;">Partner</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0;">Input (BBL)</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0;">Allocated (BBL)</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0;">Loss (BBL)</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0;">Share (%)</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #cbd5e0;">Efficiency</th>
                </tr>
            </thead>
            <tbody>
                {allocation_rows}
            </tbody>
        </table>

        <div class="divider"></div>

        <p style="font-size: 14px; color: #718096;">
            <strong>Note:</strong> This report reflects the proportional back-allocation of terminal volumes
            to each partner based on their net volume contributions for {period_month}.
            Please log into the FlowShare platform to view additional details and historical trends.
        </p>
    """

    return get_email_template(body, f"Reconciliation report for {period_month}")


def format_reconciliation_email(reconciliation_data: dict) -> str:
    """
    Format reconciliation notification email (legacy - kept for compatibility)

    Args:
        reconciliation_data: Dictionary with reconciliation details

    Returns:
        HTML formatted email body
    """
    period_start = reconciliation_data.get('period_start', '')
    period_end = reconciliation_data.get('period_end', '')
    allocations_count = reconciliation_data.get('allocations_count', 0)
    total_input = reconciliation_data.get('total_input_volume', 0)
    terminal_volume = reconciliation_data.get('terminal_volume', 0)
    shrinkage = reconciliation_data.get('shrinkage_factor', 0)
    partners = reconciliation_data.get('partners', [])

    body = f"""
        <h1>✅ New Reconciliation Report Available</h1>

        <p>Hello,</p>

        <p>A new reconciliation report has been completed for the period <strong>{period_start}</strong> to <strong>{period_end}</strong>.</p>

        <div class="highlight-box">
            <h3>📊 Reconciliation Summary</h3>
            <table class="data-table">
                <tr>
                    <td><strong>Period:</strong></td>
                    <td>{period_start} to {period_end}</td>
                </tr>
                <tr>
                    <td><strong>Partners:</strong></td>
                    <td>{allocations_count}</td>
                </tr>
                <tr>
                    <td><strong>Total Input Volume:</strong></td>
                    <td>{total_input:,.2f} bbl</td>
                </tr>
                <tr>
                    <td><strong>Terminal Volume:</strong></td>
                    <td>{terminal_volume:,.2f} bbl</td>
                </tr>
                <tr>
                    <td><strong>Shrinkage Factor:</strong></td>
                    <td>{shrinkage:.2f}%</td>
                </tr>
            </table>
        </div>

        <h2>Partners Involved</h2>
        <p>{partners}</p>

        <p style="text-align: center;">
            <a href="#" class="button">View Full Report →</a>
        </p>

        <div class="divider"></div>

        <p style="font-size: 14px; color: #718096;">
            <strong>Note:</strong> Please review the allocations in the FlowShare dashboard.
            If you have any questions or concerns, please contact your JV Coordinator.
        </p>
    """

    return get_email_template(body, f"Reconciliation report for {period_start} to {period_end}")


def format_markdown_for_email(text: str) -> str:
    """
    Convert Markdown-like text to HTML for email display

    Args:
        text: Text with markdown formatting

    Returns:
        HTML formatted text
    """
    import re

    # Convert bold (**text** to <strong>text</strong>)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    # Convert headers (## Header to <h3>Header</h3>)
    text = re.sub(r'^##\s+(.+)$', r'<h3 style="color: #2d3748; margin-top: 20px; margin-bottom: 10px;">\1</h3>', text, flags=re.MULTILINE)

    # Convert bullet points (* item to <li>item</li>)
    lines = text.split('\n')
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Bullet point
        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul style="margin: 10px 0; padding-left: 20px;">')
                in_list = True
            item_text = stripped[2:]
            formatted_lines.append(f'<li style="margin-bottom: 8px;">{item_text}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if stripped:
                formatted_lines.append(f'<p style="margin-bottom: 10px;">{stripped}</p>')
            else:
                formatted_lines.append('<br>')

    if in_list:
        formatted_lines.append('</ul>')

    return '\n'.join(formatted_lines)


def format_audit_alert_email(audit_data: dict) -> str:
    """
    Format audit alert email for flagged entries

    Args:
        audit_data: Dictionary with audit details

    Returns:
        HTML formatted email body
    """
    entry_id = audit_data.get('entry_id', '')
    partner = audit_data.get('partner', '')
    issues = audit_data.get('issues', [])
    confidence_score = audit_data.get('confidence_score', 0)
    ai_reasoning = audit_data.get('ai_reasoning', '')

    # Format issues as HTML list
    issues_html = '<ul style="margin: 10px 0; padding-left: 20px;">' + ''.join([f'<li style="margin-bottom: 8px;">{issue}</li>' for issue in issues]) + '</ul>'

    # Format AI reasoning with markdown conversion
    formatted_reasoning = format_markdown_for_email(ai_reasoning)

    body = f"""
        <h1>⚠️ Production Entry Flagged for Review</h1>

        <p>Hello,</p>

        <p>A production entry has been flagged by the FlowShare Auditor Agent and requires your attention.</p>

        <div class="highlight-box" style="border-left-color: #f59e0b;">
            <h3>🔍 Flagged Entry Details</h3>
            <table class="data-table">
                <tr>
                    <td><strong>Entry ID:</strong></td>
                    <td>{entry_id}</td>
                </tr>
                <tr>
                    <td><strong>Partner:</strong></td>
                    <td>{partner}</td>
                </tr>
                <tr>
                    <td><strong>Confidence Score:</strong></td>
                    <td>{confidence_score}%</td>
                </tr>
            </table>
        </div>

        <h2>Issues Identified</h2>
        {issues_html}

        <h2>AI Analysis</h2>
        <div class="highlight-box">
            {formatted_reasoning}
        </div>

        <p style="text-align: center;">
            <a href="#" class="button">Review Entry →</a>
        </p>

        <div class="divider"></div>

        <p style="font-size: 14px; color: #718096;">
            <strong>Action Required:</strong> Please review this entry and make necessary corrections
            or provide additional information to resolve the flagged issues.
        </p>
    """

    return get_email_template(body, f"Production entry {entry_id} flagged for review")


def format_generic_notification(title: str, message: str, action_url: str = None) -> str:
    """
    Format a generic notification email

    Args:
        title: Email title
        message: Main message content (can include markdown)
        action_url: Optional action button URL

    Returns:
        HTML formatted email body
    """
    action_button = ""
    if action_url:
        action_button = f'<p style="text-align: center;"><a href="{action_url}" class="button">Take Action →</a></p>'

    # Format message with markdown support
    formatted_message = format_markdown_for_email(message)

    body = f"""
        <h1>{title}</h1>

        <p>Hello,</p>

        {formatted_message}

        {action_button}

        <div class="divider"></div>

        <p style="font-size: 14px; color: #718096;">
            This is an automated notification from the FlowShare system.
        </p>
    """

    return get_email_template(body, title)
