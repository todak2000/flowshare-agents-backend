"""
Range Validator - Validates production data against configured ranges
KISS principle: Does one thing - checks if values are within acceptable ranges
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.models import ProductionEntry, ValidationIssue, SeverityLevel
from shared.config import config
from typing import List


class RangeValidator:
    """
    Validates production entry fields against configured ranges

    Single Responsibility: Range checking only
    """

    def validate(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """
        Validate all field ranges

        Args:
            entry: Production entry to validate

        Returns:
            List of validation issues found
        """
        issues = []

        issues.extend(self._validate_bsw(entry))
        issues.extend(self._validate_temperature(entry))
        issues.extend(self._validate_api_gravity(entry))

        return issues

    def _validate_bsw(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """Validate BSW (Basic Sediment and Water) percentage"""
        if config.BSW_MIN <= entry.bsw_percent <= config.BSW_MAX:
            return []

        severity = SeverityLevel.HIGH if entry.bsw_percent > 15 else SeverityLevel.MEDIUM

        return [ValidationIssue(
            field="bsw_percent",
            severity=severity,
            message=f"BSW {entry.bsw_percent}% outside normal range ({config.BSW_MIN}-{config.BSW_MAX}%)",
            suggestion="Verify water content measurement. High BSW may indicate water breakthrough.",
            value=entry.bsw_percent
        )]

    def _validate_temperature(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """Validate temperature in Fahrenheit"""
        if config.TEMP_MIN <= entry.temperature_degF <= config.TEMP_MAX:
            return []

        return [ValidationIssue(
            field="temperature_degF",
            severity=SeverityLevel.MEDIUM,
            message=f"Temperature {entry.temperature_degF}°F outside normal range ({config.TEMP_MIN}-{config.TEMP_MAX}°F)",
            suggestion="Check temperature sensor. Extreme temperatures affect volume calculations.",
            value=entry.temperature_degF
        )]

    def _validate_api_gravity(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """Validate API gravity"""
        if config.API_GRAVITY_MIN <= entry.api_gravity <= config.API_GRAVITY_MAX:
            return []

        return [ValidationIssue(
            field="api_gravity",
            severity=SeverityLevel.LOW,
            message=f"API Gravity {entry.api_gravity}° outside typical range ({config.API_GRAVITY_MIN}-{config.API_GRAVITY_MAX}°)",
            suggestion="Verify crude quality. Unusual API gravity may indicate contamination.",
            value=entry.api_gravity
        )]
