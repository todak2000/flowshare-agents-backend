"""
Shrinkage Calculator - Calculate shrinkage/loss factor
Accounts for volume loss between production and terminal
Based on methodology document and frontend allocation-engine.ts
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from typing import Dict, Any


class ShrinkageCalculator:
    """
    Calculates shrinkage factor to account for volume loss

    Shrinkage occurs due to:
    - Evaporation during transport
    - Measurement errors
    - Temperature changes
    - Pipeline losses

    Formula:
        Shrinkage Factor (%) = [(Total Net Volume - Terminal Volume) / Total Net Volume] × 100
    """

    def calculate_shrinkage_factor(
        self,
        total_net_volume: float,
        terminal_volume: float
    ) -> float:
        """
        Calculate shrinkage factor percentage

        Formula: Shrinkage % = [(Total Net - Terminal) / Total Net] × 100

        Args:
            total_net_volume: Total net volume from all production entries (barrels)
            terminal_volume: Volume measured at terminal (barrels)

        Returns:
            Shrinkage factor as percentage (can be negative if gain)
        """
        if total_net_volume == 0:
            logger.warning("Total net volume is zero, cannot calculate shrinkage")
            return 0.0

        shrinkage_factor = (
            (total_net_volume - terminal_volume) / total_net_volume
        ) * 100

        # Round to 2 decimal places
        shrinkage_factor = round(shrinkage_factor, 2)

        # Log warning if shrinkage is unusually high
        if abs(shrinkage_factor) > 10:
            logger.warning(
                "High shrinkage factor detected",
                shrinkage_factor=shrinkage_factor,
                total_net_volume=total_net_volume,
                terminal_volume=terminal_volume
            )

        # Log info if there's a gain (negative shrinkage)
        if shrinkage_factor < 0:
            logger.info(
                "Volume gain detected (negative shrinkage)",
                shrinkage_factor=shrinkage_factor,
                gain_volume=round(terminal_volume - total_net_volume, 2)
            )

        logger.debug(
            "Shrinkage factor calculated",
            total_net_volume=total_net_volume,
            terminal_volume=terminal_volume,
            shrinkage_factor=shrinkage_factor,
            volume_loss=round(total_net_volume - terminal_volume, 2)
        )

        return shrinkage_factor

    def calculate_volume_loss(
        self,
        total_net_volume: float,
        terminal_volume: float
    ) -> float:
        """
        Calculate absolute volume loss in barrels

        Args:
            total_net_volume: Total net volume from all production entries (barrels)
            terminal_volume: Volume measured at terminal (barrels)

        Returns:
            Volume loss in barrels (positive = loss, negative = gain)
        """
        volume_loss = total_net_volume - terminal_volume
        return round(volume_loss, 2)

    def get_shrinkage_analysis(
        self,
        total_gross_volume: float,
        total_net_volume: float,
        terminal_volume: float
    ) -> Dict[str, Any]:
        """
        Get comprehensive shrinkage analysis

        Args:
            total_gross_volume: Total gross volume before any corrections
            total_net_volume: Total net volume after all corrections
            terminal_volume: Volume measured at terminal

        Returns:
            Dictionary with detailed shrinkage analysis:
                - shrinkage_factor: Percentage shrinkage
                - volume_loss: Absolute volume loss in barrels
                - total_corrections: Total deductions from gross to net
                - terminal_variance: Difference between net and terminal
                - efficiency_rate: Terminal volume / Gross volume percentage
        """
        shrinkage_factor = self.calculate_shrinkage_factor(
            total_net_volume,
            terminal_volume
        )

        volume_loss = self.calculate_volume_loss(
            total_net_volume,
            terminal_volume
        )

        # Calculate total corrections (gross to net)
        total_corrections = total_gross_volume - total_net_volume

        # Calculate terminal variance (net to terminal)
        terminal_variance = total_net_volume - terminal_volume

        # Calculate efficiency rate (what % of gross volume reaches terminal)
        efficiency_rate = 0.0
        if total_gross_volume > 0:
            efficiency_rate = (terminal_volume / total_gross_volume) * 100

        analysis = {
            'shrinkage_factor': shrinkage_factor,
            'volume_loss': volume_loss,
            'total_gross_volume': round(total_gross_volume, 2),
            'total_net_volume': round(total_net_volume, 2),
            'terminal_volume': round(terminal_volume, 2),
            'total_corrections': round(total_corrections, 2),
            'terminal_variance': round(terminal_variance, 2),
            'efficiency_rate': round(efficiency_rate, 2)
        }

        logger.info(
            "Shrinkage analysis complete",
            **analysis
        )

        return analysis

    def validate_volumes(
        self,
        total_net_volume: float,
        terminal_volume: float
    ) -> Dict[str, Any]:
        """
        Validate volume inputs

        Args:
            total_net_volume: Total net volume
            terminal_volume: Terminal volume

        Returns:
            Validation result with any warnings
        """
        warnings = []

        if total_net_volume <= 0:
            warnings.append("Total net volume must be greater than 0")

        if terminal_volume <= 0:
            warnings.append("Terminal volume must be greater than 0")

        if terminal_volume > total_net_volume * 1.1:
            warnings.append(
                "Terminal volume exceeds net volume by >10% - possible measurement error"
            )

        shrinkage_factor = 0.0
        if total_net_volume > 0:
            shrinkage_factor = abs(
                self.calculate_shrinkage_factor(total_net_volume, terminal_volume)
            )

        if shrinkage_factor > 15:
            warnings.append(
                f"Shrinkage factor is very high ({shrinkage_factor}%) - verify measurements"
            )

        return {
            'is_valid': len(warnings) == 0,
            'warnings': warnings
        }
