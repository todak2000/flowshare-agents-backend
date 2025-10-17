"""
Accountant Agent - Allocation Calculation Orchestrator

KISS principle: Simple orchestration of modular components
DRY principle: No repeated code, delegates to specialized modules
Single Responsibility: Coordinates allocation workflow only
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import AllocationResult
from shared.firestore_client import firestore_client
from shared.config import config
from shared.logger import logger
from shared.cache import SimpleCache
from shared.utils import utc_now
from typing import Dict, Any, List
import asyncio

# Import agent-specific calculators
from calculators import OwnershipCalculator, AllocationCalculator


class AccountantAgent:
    """
    Agent 2: Allocation Calculation Agent

    Orchestrates the allocation workflow:
    1. Retrieve partner ownership data
    2. Calculate allocation percentages
    3. Validate allocations sum to 100%
    4. Save results to Firestore

    Uses composition pattern with specialized calculators
    """

    def __init__(self):
        """Initialize agent with modular components"""
        self.name = "Accountant Agent"

        # Initialize components (Dependency Injection pattern)
        self._cache = SimpleCache(max_size=100)
        self._ownership_calculator = OwnershipCalculator(self._cache)
        self._allocation_calculator = AllocationCalculator()  # Now uses full methodology

        # Metrics
        self._allocation_count = 0

        logger.info(f"{self.name} initialized with full petroleum allocation methodology")

    async def calculate_allocation(self, receipt_data: dict) -> AllocationResult:
        """
        Main allocation workflow using full petroleum methodology

        Orchestrates:
        1. Parse receipt data and production entries
        2. Calculate net volumes with all corrections (temp, API, BS&W)
        3. Calculate shrinkage factor
        4. Proportionally allocate terminal volume
        5. Validate totals
        6. Save results

        Args:
            receipt_data: Terminal receipt document with:
                - id: Receipt identifier
                - terminal_volume_bbl: Terminal volume
                - api_gravity: Terminal API gravity
                - production_entries: List of production entries with:
                    - partner: Partner name
                    - gross_volume_bbl: Gross volume
                    - bsw_percent: BS&W percentage
                    - temperature_degF: Temperature
                    - api_gravity: Observed API gravity

        Returns:
            AllocationResult with complete allocation details
        """
        start_time = utc_now()
        self._allocation_count += 1
        receipt_id = receipt_data.get('id', 'unknown')

        logger.info(
            "Starting full methodology allocation calculation",
            receipt_id=receipt_id,
            allocation_number=self._allocation_count
        )

        try:
            # Extract production entries and terminal receipt data
            production_entries = receipt_data.get('production_entries', [])

            if not production_entries:
                raise ValueError("No production entries provided in receipt data")

            terminal_receipt = {
                'terminal_volume_bbl': receipt_data.get('terminal_volume_bbl', 0),
                'api_gravity': receipt_data.get('api_gravity', 0)
            }

            # Step 1: Calculate allocations using full methodology
            # This includes: net volume calculation, shrinkage, proportional allocation
            allocation_result = self._allocation_calculator.calculate(
                production_entries=production_entries,
                terminal_receipt=terminal_receipt
            )

            # Step 2: Validate allocations
            validation_result = self._allocation_calculator.validate_allocations(
                allocation_result['allocation_results']
            )

            if not validation_result['is_valid']:
                logger.warning(
                    "Allocation validation failed",
                    receipt_id=receipt_id,
                    error=validation_result.get('error', 'Unknown error')
                )

            # Step 3: Create result
            result = AllocationResult(
                receipt_id=receipt_id,
                allocations=allocation_result['allocation_results'],
                total_allocated=allocation_result['total_allocated'],
                validation_status=validation_result['is_valid'],
                timestamp=utc_now().isoformat()
            )

            # Step 4: Save results (async, non-blocking)
            execution_time = (utc_now() - start_time).total_seconds() * 1000
            await self._save_results(receipt_id, result, execution_time)

            logger.info(
                "Full methodology allocation calculation complete",
                receipt_id=receipt_id,
                allocations_count=len(allocation_result['allocation_results']),
                total_gross=allocation_result['total_gross_volume'],
                total_net=allocation_result['total_net_volume'],
                terminal_volume=allocation_result['terminal_volume'],
                shrinkage_factor=allocation_result['shrinkage_factor'],
                execution_time_ms=round(execution_time, 2),
                cache_stats=self._cache.stats()["utilization"]
            )

            return result

        except ValueError as e:
            logger.error("Invalid receipt data", receipt_id=receipt_id, error=str(e))
            raise
        except Exception as e:
            logger.error(
                "Allocation calculation failed",
                receipt_id=receipt_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    async def _save_results(self, receipt_id: str, result: AllocationResult, execution_time: float):
        """
        Save allocation results to Firestore (async, non-blocking)

        Runs Firestore update and activity logging in parallel

        Args:
            receipt_id: Receipt identifier
            result: Allocation result
            execution_time: Execution time in milliseconds
        """
        try:
            await asyncio.gather(
                asyncio.to_thread(self._update_firestore, receipt_id, result),
                asyncio.to_thread(self._log_activity, receipt_id, result, execution_time)
            )
        except Exception as e:
            logger.error("Failed to save results", receipt_id=receipt_id, error=str(e))
            # Don't fail allocation if saving fails

    def _update_firestore(self, receipt_id: str, result: AllocationResult) -> None:
        """
        Update terminal receipt in Firestore

        Args:
            receipt_id: Receipt identifier
            result: Allocation result
        """
        update_data = {
            'allocations': result.allocations,
            'total_allocated': result.total_allocated,
            'allocation_status': 'completed' if result.validation_status else 'failed',
            'allocated_at': result.timestamp
        }

        firestore_client.update_document(
            collection=config.COLLECTION_TERMINAL_RECEIPTS,
            doc_id=receipt_id,
            data=update_data
        )

    def _log_activity(self, receipt_id: str, result: AllocationResult, execution_time: float) -> None:
        """
        Log agent activity to Firestore

        Args:
            receipt_id: Receipt identifier
            result: Allocation result
            execution_time: Execution time in milliseconds
        """
        log_data = {
            'agent_name': self.name,
            'action': 'calculate_allocation',
            'status': 'completed',
            'input_data': {'receipt_id': receipt_id},
            'output_data': {
                'allocations_count': len(result.allocations),
                'total_allocated': result.total_allocated,
                'validation_status': result.validation_status
            },
            'execution_time_ms': round(execution_time, 2),
            'timestamp': utc_now().isoformat()
        }

        firestore_client.log_agent_activity(log_data)

    # Public API for management and monitoring

    def clear_cache(self):
        """Clear cache (useful for testing or memory management)"""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics for monitoring

        Returns:
            Dictionary with agent statistics
        """
        return {
            "allocation_count": self._allocation_count,
            "cache_stats": self._cache.stats()
        }


# Singleton instance
accountant_agent = AccountantAgent()
