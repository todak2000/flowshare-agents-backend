"""
Temperature Corrector - VCF (Volume Correction Factor) calculations
Implements petroleum industry standard temperature corrections
Based on methodology document and frontend allocation-engine.ts
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict


class TemperatureCorrector:
    """
    Calculates Volume Correction Factor (VCF) based on temperature and API gravity

    Formula: VCF = 1 - α(T - Ts) - β(T - Ts)²

    Where:
        T = Observed temperature (°F)
        Ts = Standard temperature (60°F)
        α, β = Coefficients based on API gravity range
    """

    # Standard temperature per petroleum industry standards
    STANDARD_TEMP_F = 60.0

    # VCF constraints per methodology
    MIN_VCF = 0.95
    MAX_VCF = 1.05

    def get_correction_coefficients(self, api_gravity: float) -> Dict[str, float]:
        """
        Get temperature correction coefficients (α, β) based on API gravity range

        Following the methodology document's ranges and values:
        - Heavy crude (API ≤ 10): α = 0.0003, β = 0.0000001
        - Medium crude (10 < API ≤ 25): α = 0.0003-0.0004, β = 0.0000001-0.0000002
        - Light crude (25 < API ≤ 45): α = 0.0004-0.0005, β = 0.0000002-0.0000005
        - Condensate (API > 45): α = 0.0005, β = 0.0000005

        Args:
            api_gravity: API gravity in degrees API

        Returns:
            Dictionary with 'alpha' and 'beta' coefficients
        """
        if api_gravity <= 10:
            # Heavy crude
            return {'alpha': 0.0003, 'beta': 0.0000001}

        elif api_gravity <= 25:
            # Medium crude - linear interpolation
            factor = (api_gravity - 10) / 15
            return {
                'alpha': 0.0003 + factor * 0.0001,
                'beta': 0.0000001 + factor * 0.0000001
            }

        elif api_gravity <= 45:
            # Light crude - linear interpolation
            factor = (api_gravity - 25) / 20
            return {
                'alpha': 0.0004 + factor * 0.0001,
                'beta': 0.0000002 + factor * 0.0000003
            }

        else:
            # Condensate
            return {'alpha': 0.0005, 'beta': 0.0000005}

    def calculate_correction(
        self,
        observed_temp: float,
        api_gravity: float,
        standard_temp: float = None
    ) -> float:
        """
        Calculate temperature correction factor (VCF)

        Formula: VCF = 1 - α(T - Ts) - β(T - Ts)²

        Args:
            observed_temp: Observed temperature in °F
            api_gravity: API gravity in degrees API
            standard_temp: Standard temperature in °F (default: 60°F)

        Returns:
            Volume Correction Factor (VCF), constrained to [0.95, 1.05]
        """
        if standard_temp is None:
            standard_temp = self.STANDARD_TEMP_F

        # Calculate temperature difference
        temp_diff = observed_temp - standard_temp

        # Get coefficients based on API gravity
        coeffs = self.get_correction_coefficients(api_gravity)
        alpha = coeffs['alpha']
        beta = coeffs['beta']

        # Calculate VCF using methodology formula
        # VCF = 1 - α(T - Ts) - β(T - Ts)²
        vcf = 1 - alpha * temp_diff - beta * (temp_diff ** 2)

        # Apply constraints per methodology
        vcf_constrained = max(self.MIN_VCF, min(self.MAX_VCF, vcf))

        # Log if VCF was constrained
        if vcf != vcf_constrained:
            logger.warning(
                "VCF constrained to valid range",
                original_vcf=round(vcf, 6),
                constrained_vcf=round(vcf_constrained, 6),
                temp_diff=round(temp_diff, 2),
                api_gravity=api_gravity
            )

        logger.debug(
            "Temperature correction calculated",
            observed_temp=observed_temp,
            standard_temp=standard_temp,
            temp_diff=round(temp_diff, 2),
            api_gravity=api_gravity,
            alpha=alpha,
            beta=beta,
            vcf=round(vcf_constrained, 6)
        )

        return round(vcf_constrained, 6)  # 6 decimal places for precision

    def validate_temperature(self, temperature: float) -> bool:
        """
        Validate temperature is within acceptable range

        Per methodology: -50°F ≤ T ≤ 200°F

        Args:
            temperature: Temperature in °F

        Returns:
            True if valid, False otherwise
        """
        return -50 <= temperature <= 200
