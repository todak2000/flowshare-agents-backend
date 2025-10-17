"""
API Gravity Corrector - API gravity corrections
Implements petroleum industry standard API gravity corrections
Based on methodology document and frontend allocation-engine.ts
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger


class APICorrector:
    """
    Calculates API gravity correction factor

    Adjusts for difference between observed and terminal (standard) API gravity
    using specific gravity conversion formulas

    Formula:
        Observed SG = 141.5 / (Observed API + 131.5)
        Standard SG = 141.5 / (Terminal API + 131.5)
        API Correction = Standard SG / Observed SG
    """

    # API Correction constraints per methodology
    MIN_CORRECTION = 0.9
    MAX_CORRECTION = 1.15

    def calculate_specific_gravity(self, api_gravity: float) -> float:
        """
        Convert API gravity to specific gravity

        Formula: SG = 141.5 / (API + 131.5)

        Args:
            api_gravity: API gravity in degrees API

        Returns:
            Specific gravity (dimensionless)
        """
        return 141.5 / (api_gravity + 131.5)

    def calculate_correction(
        self,
        observed_api: float,
        terminal_api: float
    ) -> float:
        """
        Calculate API gravity correction factor

        Converts both API gravities to specific gravities, then calculates ratio

        Formula: API Correction = Standard SG / Observed SG

        Args:
            observed_api: Observed API gravity (from production entry)
            terminal_api: Terminal/standard API gravity (from terminal receipt)

        Returns:
            API correction factor, constrained to [0.9, 1.15]
        """
        # Calculate specific gravities
        observed_sg = self.calculate_specific_gravity(observed_api)
        standard_sg = self.calculate_specific_gravity(terminal_api)

        # Calculate correction factor
        # API Correction = Standard SG / Observed SG (as per methodology)
        correction = standard_sg / observed_sg

        # Apply constraints per methodology
        correction_constrained = max(
            self.MIN_CORRECTION,
            min(self.MAX_CORRECTION, correction)
        )

        # Log if correction was constrained
        if correction != correction_constrained:
            logger.warning(
                "API correction constrained to valid range",
                original_correction=round(correction, 6),
                constrained_correction=round(correction_constrained, 6),
                observed_api=observed_api,
                terminal_api=terminal_api
            )

        logger.debug(
            "API gravity correction calculated",
            observed_api=observed_api,
            terminal_api=terminal_api,
            observed_sg=round(observed_sg, 6),
            standard_sg=round(standard_sg, 6),
            correction=round(correction_constrained, 6)
        )

        return round(correction_constrained, 6)  # 6 decimal places for precision

    def validate_api_gravity(self, api_gravity: float) -> bool:
        """
        Validate API gravity is within acceptable range

        Per methodology: 10 ≤ API ≤ 45 degrees

        Args:
            api_gravity: API gravity in degrees API

        Returns:
            True if valid, False otherwise
        """
        return 10 <= api_gravity <= 45
