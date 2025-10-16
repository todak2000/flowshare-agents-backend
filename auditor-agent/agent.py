"""
Auditor Agent - Production Entry Validation Orchestrator

KISS principle: Simple orchestration of modular components
DRY principle: No repeated code, delegates to specialized modules
Single Responsibility: Coordinates validation workflow only
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import ProductionEntry, ValidationResult, ValidationStatus
from shared.gemini_client import gemini_client
from shared.firestore_client import firestore_client
from shared.config import config
from shared.logger import logger
from typing import Dict, Any
import asyncio

# Import modular components
from cache import SimpleCache
from validators import RangeValidator, AnomalyDetector
from utils import utc_now


class AuditorAgent:
    """
    Agent 1: Data Validation Agent

    Orchestrates the validation workflow:
    1. Range validation
    2. Anomaly detection
    3. AI analysis
    4. Firestore updates

    Uses composition pattern with specialized validators
    """

    def __init__(self):
        """Initialize agent with modular components"""
        self.name = "Auditor Agent"

        # Initialize components (Dependency Injection pattern)
        self._cache = SimpleCache(max_size=100)
        self._range_validator = RangeValidator()
        self._anomaly_detector = AnomalyDetector(self._cache)

        # Metrics
        self._validation_count = 0

        logger.info(f"{self.name} initialized with modular components")

    async def validate_entry(self, entry_data: dict) -> ValidationResult:
        """
        Main validation workflow

        Orchestrates:
        1. Data parsing and validation (Pydantic)
        2. Range checks (RangeValidator)
        3. Anomaly detection (AnomalyDetector)
        4. AI analysis (Gemini)
        5. Results storage (Firestore)

        Args:
            entry_data: Production entry document from Firestore

        Returns:
            ValidationResult with status and issues
        """
        start_time = utc_now()
        self._validation_count += 1
        entry_id = entry_data.get('id', 'unknown')

        logger.info(
            "Starting validation",
            entry_id=entry_id,
            validation_number=self._validation_count
        )

        try:
            # Step 1: Parse and validate with Pydantic
            entry = ProductionEntry(**entry_data)

            # Step 2: Run validations (modular validators)
            issues = []

            # Range validation (fast, synchronous)
            range_issues = self._range_validator.validate(entry)
            issues.extend(range_issues)

            # Anomaly detection (with caching)
            anomaly_issues = await self._anomaly_detector.detect(entry)
            issues.extend(anomaly_issues)

            # Step 3: AI analysis (with timeout and fallback)
            ai_analysis = await self._get_ai_analysis(entry_data, issues, entry_id)

            # Step 4: Determine status and confidence
            status_value, flagged = self._determine_status(issues)
            confidence_score = self._calculate_confidence(issues)

            # Step 5: Create result
            result = ValidationResult(
                entry_id=entry_id,
                status=status_value,
                flagged=flagged,
                issues=issues,
                ai_analysis=ai_analysis,
                confidence_score=confidence_score,
                timestamp=utc_now().isoformat()
            )

            # Step 6: Save results (async, non-blocking)
            execution_time = (utc_now() - start_time).total_seconds() * 1000
            await self._save_results(entry_id, result, execution_time)

            logger.info(
                "Validation complete",
                entry_id=entry_id,
                status=status_value,
                issues_count=len(issues),
                execution_time_ms=round(execution_time, 2),
                cache_stats=self._cache.stats()["utilization"]
            )

            return result

        except ValueError as e:
            logger.error("Invalid entry data", entry_id=entry_id, error=str(e))
            raise
        except Exception as e:
            logger.error(
                "Validation failed",
                entry_id=entry_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    async def _get_ai_analysis(self, entry_data: dict, issues: list, entry_id: str) -> str:
        """
        Get AI analysis with timeout and fallback

        Args:
            entry_data: Production entry data
            issues: List of validation issues
            entry_id: Entry identifier

        Returns:
            AI analysis text or fallback message
        """
        try:
            ai_analysis = await asyncio.wait_for(
                gemini_client.analyze_production_data(
                    entry_data=entry_data,
                    issues=[issue.dict() for issue in issues]
                ),
                timeout=15.0  # 15 second timeout
            )
            return ai_analysis
        except asyncio.TimeoutError:
            logger.warning("AI analysis timeout, using fallback", entry_id=entry_id)
            return "AI analysis timed out. Manual review recommended."
        except Exception as e:
            logger.error("AI analysis failed", entry_id=entry_id, error=str(e))
            return f"AI analysis unavailable: {str(e)}"

    async def _save_results(self, entry_id: str, result: ValidationResult, execution_time: float):
        """
        Save validation results to Firestore (async, non-blocking)

        Runs Firestore update and activity logging in parallel

        Args:
            entry_id: Entry identifier
            result: Validation result
            execution_time: Execution time in milliseconds
        """
        try:
            await asyncio.gather(
                asyncio.to_thread(self._update_firestore, entry_id, result),
                asyncio.to_thread(self._log_activity, entry_id, result, execution_time)
            )
        except Exception as e:
            logger.error("Failed to save results", entry_id=entry_id, error=str(e))
            # Don't fail validation if saving fails

    def _determine_status(self, issues: list) -> tuple:
        """
        Determine validation status based on issues

        Args:
            issues: List of validation issues

        Returns:
            Tuple of (status, flagged)
        """
        from shared.models import SeverityLevel

        high_severity_count = len([i for i in issues if i.severity == SeverityLevel.HIGH])

        if high_severity_count > 0:
            return ValidationStatus.FLAGGED, True
        elif len(issues) > 0:
            return ValidationStatus.WARNING, False
        else:
            return ValidationStatus.VALID, False

    def _calculate_confidence(self, issues: list) -> float:
        """
        Calculate confidence score (0-100)

        Deducts points based on issue severity:
        - LOW: -5 points
        - MEDIUM: -15 points
        - HIGH: -30 points

        Args:
            issues: List of validation issues

        Returns:
            Confidence score (0-100)
        """
        if not issues:
            return 100.0

        from shared.models import SeverityLevel

        severity_weights = {
            SeverityLevel.LOW: 5,
            SeverityLevel.MEDIUM: 15,
            SeverityLevel.HIGH: 30
        }

        total_deduction = sum(severity_weights.get(issue.severity, 10) for issue in issues)
        return max(0.0, 100.0 - total_deduction)

    def _update_firestore(self, entry_id: str, result: ValidationResult) -> None:
        """
        Update production entry in Firestore

        Args:
            entry_id: Entry identifier
            result: Validation result
        """
        update_data = {
            'flagged': result.flagged,
            'validation_status': result.status,
            'ai_reason': result.ai_analysis,
            'confidence_score': result.confidence_score,
            'validated_at': result.timestamp
        }

        firestore_client.update_document(
            collection=config.COLLECTION_PRODUCTION_ENTRIES,
            doc_id=entry_id,
            data=update_data
        )

    def _log_activity(self, entry_id: str, result: ValidationResult, execution_time: float) -> None:
        """
        Log agent activity to Firestore

        Args:
            entry_id: Entry identifier
            result: Validation result
            execution_time: Execution time in milliseconds
        """
        log_data = {
            'agent_name': self.name,
            'action': 'validate_production_entry',
            'status': 'completed',
            'input_data': {'entry_id': entry_id},
            'output_data': {
                'status': result.status,
                'flagged': result.flagged,
                'issues_count': len(result.issues)
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
            "validation_count": self._validation_count,
            "cache_stats": self._cache.stats()
        }


# Singleton instance
auditor_agent = AuditorAgent()
