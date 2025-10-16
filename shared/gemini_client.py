"""
Gemini API client for all agents
"""
from google import genai
from google.genai.types import GenerateContentConfig
from typing import Optional, Dict, Any
from .config import config
from .logger import logger


class GeminiClient:
    """Wrapper for Gemini API operations"""

    def __init__(self):
        """Initialize Gemini client"""
        # Check if API key is set
        if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "":
            raise ValueError(
                "\n\n❌ GEMINI_API_KEY not set!\n\n"
                "To fix this:\n"
                "1. Get your API key from: https://aistudio.google.com/app/apikey\n"
                "2. Set environment variable:\n"
                "   export GEMINI_API_KEY='your-api-key-here'\n\n"
                "Or create a .env file with:\n"
                "   GEMINI_API_KEY=your-api-key-here\n"
                "   Then run: export $(cat .env | xargs)\n"
            )

        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model_id = config.GEMINI_MODEL
        logger.info(f"Gemini client initialized with model: {self.model_id}")

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_output_tokens: int = 1000,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content using Gemini

        Args:
            prompt: The prompt to send to Gemini
            temperature: Creativity level (0.0 - 1.0)
            max_output_tokens: Maximum response length
            system_instruction: Optional system instruction

        Returns:
            Generated text response
        """
        try:
            config_obj = GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                system_instruction=system_instruction
            )

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=config_obj
            )

            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def analyze_production_data(
        self,
        entry_data: Dict[str, Any],
        issues: list
    ) -> str:
        """
        Specialized method for Auditor Agent
        Analyzes production data for anomalies
        """
        prompt = f"""
You are an expert oil & gas production data analyst. Analyze this production entry:

**Production Data:**
{self._format_dict(entry_data)}

**Issues Found:**
{self._format_list(issues) if issues else "No issues detected"}

**Tasks:**
1. Assess overall data quality (0-100 score)
2. Identify any additional concerns beyond the flagged issues
3. Provide actionable recommendations for the field operator
4. Assign risk level: LOW, MEDIUM, or HIGH

**Format:** Provide a concise analysis in 2-3 sentences, then state the risk level.
"""

        system_instruction = "You are a production data validator with expertise in oil & gas operations. Provide clear, actionable insights."

        return await self.generate_content(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=300,
            system_instruction=system_instruction
        )

    async def generate_reconciliation_summary(
        self,
        recon_data: Dict[str, Any]
    ) -> str:
        """
        Specialized method for Communicator Agent
        Generates human-readable reconciliation summary
        """
        prompt = f"""
You are a financial analyst preparing a reconciliation report for oil & gas joint venture partners.

**Reconciliation Data:**
{self._format_dict(recon_data)}

**Tasks:**
1. Summarize the reconciliation results in clear business language
2. Highlight any significant variances
3. Explain what each partner should expect
4. Note any action items

**Format:** Write a professional 3-4 sentence summary suitable for emailing to partners.
"""

        system_instruction = "You are a professional business communicator specializing in oil & gas joint ventures."

        return await self.generate_content(
            prompt=prompt,
            temperature=0.4,
            max_output_tokens=500,
            system_instruction=system_instruction
        )

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary for prompt"""
        return "\n".join([f"  - {k}: {v}" for k, v in data.items()])

    def _format_list(self, items: list) -> str:
        """Format list for prompt"""
        if not items:
            return "None"
        return "\n".join([f"  - {item}" for item in items])


# Singleton instance
gemini_client = GeminiClient()
