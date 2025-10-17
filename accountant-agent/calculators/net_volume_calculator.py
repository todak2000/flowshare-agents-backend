"""
Net Volume Calculator - Multi-factor net volume calculation
Combines all correction factors to calculate net volume
Based on methodology document and frontend allocation-engine.ts
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict, Any
from .temperature_corrector import TemperatureCorrector
from .api_corrector import APICorrector


class NetVolumeCalculator:
    """
    Calculates net volume using all correction factors

    Formula:
        Net Volume = Gross Volume × Water Cut Factor × Temperature Correction × API Correction

    Where:
        Water Cut Factor = 1 - (BSW% / 100)
        Temperature Correction = VCF (from TemperatureCorrector)
        API Correction = from APICorrector
    """

    def __init__(self):
        """Initialize with temperature and API correctors"""
        self.temp_corrector = TemperatureCorrector()
        self.api_corrector = APICorrector()

    def calculate_water_cut_factor(self, bsw_percent: float) -> float:
        """
        Calculate water cut factor from BS&W percentage

        BS&W (Basic Sediment and Water) is the percentage of non-oil content

        Formula: Water Cut Factor = 1 - (BSW% / 100)

        Args:
            bsw_percent: BS&W percentage (0-99.99)

        Returns:
            Water cut factor (0-1)
        """
        if not (0 <= bsw_percent < 100):
            logger.warning(
                "BS&W percentage out of range",
                bsw_percent=bsw_percent
            )
            # Constrain to valid range
            bsw_percent = max(0, min(99.99, bsw_percent))

        return 1 - (bsw_percent / 100)

    def calculate_net_volume(
        self,
        gross_volume: float,
        bsw_percent: float,
        temperature_degf: float,
        observed_api: float,
        terminal_api: float
    ) -> Dict[str, Any]:
        """
        Calculate net volume with all correction factors

        Complete formula per methodology:
        Net Volume = Gross Volume × Water Cut Factor × Temp Correction × API Correction

        Args:
            gross_volume: Gross volume in barrels
            bsw_percent: BS&W percentage (0-99.99)
            temperature_degf: Observed temperature in °F
            observed_api: Observed API gravity (from entry)
            terminal_api: Terminal/standard API gravity (from receipt)

        Returns:
            Dictionary with:
                - net_volume: Final net volume in barrels
                - water_cut_factor: Applied water cut factor
                - temp_correction: Applied temperature correction (VCF)
                - api_correction: Applied API gravity correction
                - gross_volume: Original gross volume
        """
        # Step 1: Calculate Water Cut Factor
        water_cut_factor = self.calculate_water_cut_factor(bsw_percent)

        # Step 2: Calculate Temperature Correction (VCF)
        temp_correction = self.temp_corrector.calculate_correction(
            observed_temp=temperature_degf,
            api_gravity=observed_api
        )

        # Step 3: Calculate API Gravity Correction
        api_correction = self.api_corrector.calculate_correction(
            observed_api=observed_api,
            terminal_api=terminal_api
        )

        # Step 4: Apply all corrections to calculate net volume
        net_volume = (
            gross_volume *
            water_cut_factor *
            temp_correction *
            api_correction
        )

        # Round to 2 decimal places (standard for volumes in barrels)
        net_volume = round(net_volume, 2)

        logger.info(
            "Net volume calculated",
            gross_volume=gross_volume,
            bsw_percent=bsw_percent,
            temperature=temperature_degf,
            observed_api=observed_api,
            terminal_api=terminal_api,
            water_cut_factor=round(water_cut_factor, 6),
            temp_correction=round(temp_correction, 6),
            api_correction=round(api_correction, 6),
            net_volume=net_volume
        )

        return {
            'net_volume': net_volume,
            'gross_volume': gross_volume,
            'water_cut_factor': round(water_cut_factor, 6),
            'temp_correction': round(temp_correction, 6),
            'api_correction': round(api_correction, 6),
            'bsw_deduction': round(gross_volume - (gross_volume * water_cut_factor), 2),
            'temperature_adjustment': round(
                gross_volume * water_cut_factor * (1 - temp_correction), 2
            ),
            'api_adjustment': round(
                gross_volume * water_cut_factor * temp_correction * (1 - api_correction), 2
            )
        }

    def validate_inputs(
        self,
        gross_volume: float,
        bsw_percent: float,
        temperature_degf: float,
        api_gravity: float
    ) -> Dict[str, Any]:
        """
        Validate all input parameters per methodology constraints

        Args:
            gross_volume: Gross volume in barrels
            bsw_percent: BS&W percentage
            temperature_degf: Temperature in °F
            api_gravity: API gravity in degrees

        Returns:
            Dictionary with:
                - is_valid: True if all inputs valid
                - errors: List of validation errors (if any)
        """
        errors = []

        # Validate gross volume
        if gross_volume <= 0:
            errors.append("Gross volume must be greater than 0")

        # Validate BS&W percentage (0 ≤ BSW < 100)
        if not (0 <= bsw_percent < 100):
            errors.append("BS&W percentage must be between 0 and 99.99")

        # Validate temperature (-50°F ≤ T ≤ 200°F per methodology)
        if not self.temp_corrector.validate_temperature(temperature_degf):
            errors.append("Temperature must be between -50°F and 200°F")

        # Validate API gravity (10 ≤ API ≤ 45 per methodology)
        if not self.api_corrector.validate_api_gravity(api_gravity):
            errors.append("API Gravity must be between 10 and 45 degrees")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
