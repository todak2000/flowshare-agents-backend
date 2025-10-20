"""
AI Report Generator
Generates executive summaries for reconciliation reports using Gemini API
"""
import os
import httpx
from typing import Dict, Any, List
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from shared.logger import logger
from shared.config import config


class AIReportGenerator:
    """Generate AI-powered executive summaries for reconciliation reports"""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        # Use model from config (defaults to gemini-2.0-flash-exp)
        model_name = config.GEMINI_MODEL
        self.api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent'

    async def generate_reconciliation_summary(self, reconciliation_data: Dict[str, Any]) -> str:
        """
        Generate an AI-powered executive summary of reconciliation results

        Args:
            reconciliation_data: Reconciliation data including allocations, volumes, etc.

        Returns:
            HTML-formatted executive summary
        """
        try:
            if not self.api_key:
                logger.warning("Gemini API key not configured, using fallback summary")
                return self._generate_fallback_summary(reconciliation_data)

            # Prepare allocation data
            allocations = reconciliation_data.get('allocations', [])
            period_month = reconciliation_data.get('period_month', 'Unknown Period')
            total_input = reconciliation_data.get('total_input_volume', 0)
            terminal_volume = reconciliation_data.get('terminal_volume', 0)
            shrinkage = reconciliation_data.get('shrinkage_factor', 0)

            # Create prompt for Gemini
            prompt = f"""You are an oil & gas industry analyst preparing an executive summary for a Joint Venture reconciliation report.

**Reconciliation Period**: {period_month}
**Total Input Volume**: {total_input:,.2f} BBL
**Terminal Volume**: {terminal_volume:,.2f} BBL
**Overall Shrinkage Factor**: {shrinkage:.2f}% (THIS IS THE TOTAL SHRINKAGE FOR THE ENTIRE OPERATION)

**Partner Allocations**:
{self._format_allocations_for_prompt(allocations)}

IMPORTANT CLARIFICATIONS:
- The "Share" percentage (e.g., 32.60%) represents each partner's ALLOCATION PERCENTAGE of the total production, NOT their percentage of shrinkage
- Shrinkage is calculated as a TOTAL for the operation ({shrinkage:.2f}%), not per partner
- Volume Loss (in BBL) is the actual barrels lost by each partner due to the overall shrinkage factor being applied proportionally
- DO NOT confuse a partner's allocation percentage with their "percentage of total shrinkage" - these are completely different metrics

Generate a professional executive summary in HTML format (max 300 words) that:
1. Summarizes the reconciliation period and total volumes
2. Highlights each partner's ALLOCATION SHARE (their percentage of total production)
3. Comments on the OVERALL shrinkage factor ({shrinkage:.2f}%) and what it means for the operation
4. If discussing volume losses, mention the BBL amount lost by each partner (proportional to their share)
5. DO NOT say things like "Partner X contributed Y% to total shrinkage" or "representing Z% of shrinkage" - those statements are incorrect
6. Uses professional oil & gas industry terminology

Format using HTML tags (<h3>, <p>, <ul>, <li>, <strong>) for structure.
Do NOT include a title heading - start directly with the summary content.
Be concise and business-focused."""

            # Call Gemini API
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.api_url}?key={self.api_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 500,
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    summary = result['candidates'][0]['content']['parts'][0]['text']
                    logger.info("AI summary generated successfully")
                    return summary
                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return self._generate_fallback_summary(reconciliation_data)

        except Exception as e:
            logger.error(f"AI report generation failed: {str(e)}")
            return self._generate_fallback_summary(reconciliation_data)

    def _format_allocations_for_prompt(self, allocations: List[Dict]) -> str:
        """Format allocation data for AI prompt"""
        lines = []
        for alloc in allocations:
            partner = alloc.get('partner', 'Unknown')
            input_vol = alloc.get('input_volume', 0)
            allocated = alloc.get('allocated_volume', 0)
            loss = alloc.get('volume_loss', 0)
            pct = alloc.get('percentage', 0)

            lines.append(
                f"- {partner}: Input {input_vol:,.2f} BBL → Allocated {allocated:,.2f} BBL "
                f"(Loss: {loss:,.2f} BBL, Share: {pct:.2f}%)"
            )

        return "\n".join(lines)

    def _generate_fallback_summary(self, reconciliation_data: Dict[str, Any]) -> str:
        """Generate a basic summary when AI is unavailable"""
        period = reconciliation_data.get('period_month', 'Unknown Period')
        total_input = reconciliation_data.get('total_input_volume', 0)
        terminal = reconciliation_data.get('terminal_volume', 0)
        shrinkage = reconciliation_data.get('shrinkage_factor', 0)
        partners = reconciliation_data.get('allocations_count', 0)

        return f"""
<p><strong>Reconciliation completed for {period}</strong></p>

<p>This reconciliation processed production data from {partners} joint venture partners,
with a total input volume of {total_input:,.2f} BBL and terminal volume of {terminal:,.2f} BBL.</p>

<p>The overall shrinkage factor of {abs(shrinkage):.2f}% reflects the difference between
input volumes and terminal receipts, distributed proportionally across all partners based on their net volume contributions.</p>

<p><strong>Key Metrics:</strong></p>
<ul>
<li>Total Partners: {partners}</li>
<li>Combined Input: {total_input:,.2f} BBL</li>
<li>Terminal Volume: {terminal:,.2f} BBL</li>
<li>Volume Variance: {abs(shrinkage):.2f}%</li>
</ul>

<p>Please review the detailed allocation breakdown in the attached report for your specific allocation and volume adjustments.</p>
"""


# Singleton instance
ai_report_generator = AIReportGenerator()
