"""
Allocation Calculator - Full petroleum allocation methodology
Implements complete allocation workflow with all correction factors
Based on methodology document and frontend allocation-engine.ts

UPGRADED: Now includes temperature correction, API correction, BS&W deduction,
shrinkage calculation, and proportional allocation by net volume.
"""
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for shared module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.logger import logger
from .net_volume_calculator import NetVolumeCalculator
from .shrinkage_calculator import ShrinkageCalculator


class AllocationCalculator:
    """
    Calculates allocation volumes using full petroleum industry methodology

    Complete Workflow:
    1. Calculate net volumes for each production entry (with all corrections)
    2. Calculate total net volume and shrinkage factor
    3. Proportionally allocate terminal volume based on net volume percentages
    4. Calculate volume losses for each partner
    """

    def __init__(self):
        """Initialize with net volume and shrinkage calculators"""
        self.net_volume_calc = NetVolumeCalculator()
        self.shrinkage_calc = ShrinkageCalculator()

    def calculate(
        self,
        production_entries: List[Dict[str, Any]],
        terminal_receipt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate allocations using full methodology

        Complete Formula:
        1. Net Volume = Gross × (1 - BSW/100) × Temp Correction × API Correction
        2. Partner % = (Partner Net / Total Net) × 100
        3. Partner Allocated = Terminal Volume × (Partner Net / Total Net)
        4. Volume Loss = Partner Gross - Partner Allocated

        Args:
            production_entries: List of production entry dictionaries with:
                - partner: Partner name
                - gross_volume_bbl: Gross volume in barrels
                - bsw_percent: BS&W percentage
                - temperature_degF: Observed temperature
                - api_gravity: Observed API gravity
            terminal_receipt: Terminal receipt dictionary with:
                - terminal_volume_bbl: Final volume at terminal
                - api_gravity: Terminal/standard API gravity

        Returns:
            Complete allocation result with:
                - allocation_results: List of partner allocations
                - total_gross_volume: Sum of all gross volumes
                - total_net_volume: Sum of all net volumes
                - terminal_volume: Terminal volume
                - shrinkage_factor: Shrinkage percentage
                - shrinkage_analysis: Detailed analysis
        """
        if not production_entries:
            raise ValueError("No production entries provided for allocation")

        terminal_volume = terminal_receipt.get('terminal_volume_bbl', 0)
        terminal_api = terminal_receipt.get('api_gravity', 0)

        if terminal_volume <= 0:
            raise ValueError("Terminal volume must be greater than 0")

        if terminal_api <= 0:
            raise ValueError("Terminal API gravity must be greater than 0")

        # Step 1: Calculate net volumes for each production entry
        net_volume_results = []
        total_gross_volume = 0.0
        total_net_volume = 0.0

        for entry in production_entries:
            partner = entry.get('partner')
            gross_volume = entry.get('gross_volume_bbl', 0)
            bsw_percent = entry.get('bsw_percent', 0)
            temperature = entry.get('temperature_degF', 60)
            observed_api = entry.get('api_gravity', terminal_api)

            # Validate inputs
            validation = self.net_volume_calc.validate_inputs(
                gross_volume=gross_volume,
                bsw_percent=bsw_percent,
                temperature_degf=temperature,
                api_gravity=observed_api
            )

            if not validation['is_valid']:
                logger.warning(
                    "Invalid production entry inputs",
                    partner=partner,
                    errors=validation['errors']
                )
                raise ValueError(f"Invalid inputs for partner {partner}: {', '.join(validation['errors'])}")

            # Calculate net volume with all corrections
            net_result = self.net_volume_calc.calculate_net_volume(
                gross_volume=gross_volume,
                bsw_percent=bsw_percent,
                temperature_degf=temperature,
                observed_api=observed_api,
                terminal_api=terminal_api
            )

            net_volume_results.append({
                'partner': partner,
                'gross_volume': gross_volume,
                'net_volume': net_result['net_volume'],
                'water_cut_factor': net_result['water_cut_factor'],
                'temp_correction': net_result['temp_correction'],
                'api_correction': net_result['api_correction'],
                'bsw_deduction': net_result['bsw_deduction'],
                'temperature_adjustment': net_result['temperature_adjustment'],
                'api_adjustment': net_result['api_adjustment']
            })

            total_gross_volume += gross_volume
            total_net_volume += net_result['net_volume']

        # Step 2: Calculate shrinkage factor
        shrinkage_analysis = self.shrinkage_calc.get_shrinkage_analysis(
            total_gross_volume=total_gross_volume,
            total_net_volume=total_net_volume,
            terminal_volume=terminal_volume
        )

        # Step 3: Proportional allocation by net volume
        # Formula: Partner Allocated = Terminal Volume × (Partner Net / Total Net)
        allocation_results = []

        for result in net_volume_results:
            partner = result['partner']
            gross_volume = result['gross_volume']
            net_volume = result['net_volume']

            # Calculate partner percentage based on net volume
            percentage = 0.0
            if total_net_volume > 0:
                percentage = (net_volume / total_net_volume) * 100

            # Calculate allocated volume (proportional to net volume)
            allocated_volume = 0.0
            if total_net_volume > 0:
                allocated_volume = terminal_volume * (net_volume / total_net_volume)

            # Calculate volume loss (gross - allocated)
            volume_loss = gross_volume - allocated_volume

            allocation_results.append({
                'partner': partner,
                'gross_volume': round(gross_volume, 2),
                'net_volume': round(net_volume, 2),
                'allocated_volume': round(allocated_volume, 2),
                'percentage': round(percentage, 2),
                'volume_loss': round(volume_loss, 2),
                'water_cut_factor': result['water_cut_factor'],
                'temp_correction': result['temp_correction'],
                'api_correction': result['api_correction'],
                'bsw_deduction': round(result['bsw_deduction'], 2),
                'temperature_adjustment': round(result['temperature_adjustment'], 2),
                'api_adjustment': round(result['api_adjustment'], 2)
            })

        # Validate allocations sum correctly
        total_allocated = sum(a['allocated_volume'] for a in allocation_results)
        allocation_variance = abs(total_allocated - terminal_volume)

        if allocation_variance > 0.01:  # Allow small rounding errors
            logger.warning(
                "Allocation total doesn't match terminal volume",
                total_allocated=round(total_allocated, 2),
                terminal_volume=terminal_volume,
                variance=round(allocation_variance, 2)
            )

        logger.info(
            "Allocation calculation complete",
            partners_count=len(allocation_results),
            total_gross_volume=round(total_gross_volume, 2),
            total_net_volume=round(total_net_volume, 2),
            terminal_volume=terminal_volume,
            shrinkage_factor=shrinkage_analysis['shrinkage_factor'],
            total_allocated=round(total_allocated, 2)
        )

        return {
            'allocation_results': allocation_results,
            'total_gross_volume': round(total_gross_volume, 2),
            'total_net_volume': round(total_net_volume, 2),
            'terminal_volume': terminal_volume,
            'shrinkage_factor': shrinkage_analysis['shrinkage_factor'],
            'shrinkage_analysis': shrinkage_analysis,
            'total_allocated': round(total_allocated, 2),
            'allocation_variance': round(allocation_variance, 2)
        }

    def validate_allocations(self, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that allocations are correct

        Args:
            allocations: List of allocation records

        Returns:
            Validation result with status and any errors
        """
        if not allocations:
            return {
                'is_valid': False,
                'error': 'No allocations provided'
            }

        # Check all volumes are non-negative
        all_non_negative = all(
            a.get('allocated_volume', 0) >= 0 and
            a.get('gross_volume', 0) >= 0 and
            a.get('net_volume', 0) >= 0
            for a in allocations
        )

        # Check percentages sum to 100%
        total_percentage = sum(a.get('percentage', 0) for a in allocations)
        percentage_valid = abs(total_percentage - 100.0) < 0.01  # Allow small floating point errors

        # Check net volumes are less than or equal to gross volumes
        net_less_than_gross = all(
            a.get('net_volume', 0) <= a.get('gross_volume', 0)
            for a in allocations
        )

        is_valid = percentage_valid and all_non_negative and net_less_than_gross

        result = {
            'is_valid': is_valid,
            'total_percentage': round(total_percentage, 2),
            'percentage_valid': percentage_valid,
            'all_non_negative': all_non_negative,
            'net_less_than_gross': net_less_than_gross
        }

        if not is_valid:
            errors = []
            if not percentage_valid:
                errors.append(f"Percentages sum to {total_percentage}%, not 100%")
            if not all_non_negative:
                errors.append("Some volumes are negative")
            if not net_less_than_gross:
                errors.append("Net volume exceeds gross volume for some entries")
            result['error'] = "; ".join(errors)

        return result
