"""
Auditor Agent - Data Validation Logic
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import (
    ProductionEntry,
    ValidationResult,
    ValidationIssue,
    ValidationStatus,
    SeverityLevel
)
from shared.gemini_client import gemini_client
from shared.firestore_client import firestore_client
from shared.config import config
from shared.logger import logger
from typing import List, Tuple
from datetime import datetime
import statistics


class AuditorAgent:
    """
    Agent 1: Data Validation Agent
    Validates production entries and detects anomalies
    """

    def __init__(self):
        self.name = "Auditor Agent"
        logger.info(f"{self.name} initialized")

    async def validate_entry(self, entry_data: dict) -> ValidationResult:
        """
        Main validation method

        Args:
            entry_data: Production entry document from Firestore

        Returns:
            ValidationResult with status and issues
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting validation for entry", entry_id=entry_data.get('id'))

        try:
            # Parse entry
            entry = ProductionEntry(**entry_data)

            # Run validation checks
            issues = []

            # 1. Range validations
            issues.extend(self._validate_ranges(entry))

            # 2. Anomaly detection
            anomaly_issues = await self._detect_anomalies(entry)
            issues.extend(anomaly_issues)

            # 3. Get AI analysis
            ai_analysis = await gemini_client.analyze_production_data(
                entry_data=entry_data,
                issues=[issue.dict() for issue in issues]
            )

            # Determine status
            status, flagged = self._determine_status(issues)

            # Calculate confidence score
            confidence_score = self._calculate_confidence(issues)

            # Create result
            result = ValidationResult(
                entry_id=entry_data['id'],
                status=status,
                flagged=flagged,
                issues=issues,
                ai_analysis=ai_analysis,
                confidence_score=confidence_score,
                timestamp=datetime.utcnow().isoformat()
            )

            # Update Firestore
            self._update_firestore(entry_data['id'], result)

            # Log activity
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._log_activity(entry_data['id'], result, execution_time)

            logger.info(
                f"Validation complete",
                entry_id=entry_data['id'],
                status=status,
                issues_count=len(issues),
                execution_time_ms=execution_time
            )

            return result

        except Exception as e:
            logger.error(f"Validation failed", entry_id=entry_data.get('id'), error=str(e))
            raise

    def _validate_ranges(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """Validate field ranges"""
        issues = []

        # BSW %
        if not (config.BSW_MIN <= entry.bsw_percent <= config.BSW_MAX):
            severity = SeverityLevel.HIGH if entry.bsw_percent > 15 else SeverityLevel.MEDIUM
            issues.append(ValidationIssue(
                field="bsw_percent",
                severity=severity,
                message=f"BSW {entry.bsw_percent}% outside normal range ({config.BSW_MIN}-{config.BSW_MAX}%)",
                suggestion="Verify water content measurement. High BSW may indicate water breakthrough.",
                value=entry.bsw_percent
            ))

        # Temperature
        if not (config.TEMP_MIN <= entry.temperature_degF <= config.TEMP_MAX):
            issues.append(ValidationIssue(
                field="temperature_degF",
                severity=SeverityLevel.MEDIUM,
                message=f"Temperature {entry.temperature_degF}°F outside normal range ({config.TEMP_MIN}-{config.TEMP_MAX}°F)",
                suggestion="Check temperature sensor. Extreme temperatures affect volume calculations.",
                value=entry.temperature_degF
            ))

        # API Gravity
        if not (config.API_GRAVITY_MIN <= entry.api_gravity <= config.API_GRAVITY_MAX):
            issues.append(ValidationIssue(
                field="api_gravity",
                severity=SeverityLevel.LOW,
                message=f"API Gravity {entry.api_gravity}° outside typical range ({config.API_GRAVITY_MIN}-{config.API_GRAVITY_MAX}°)",
                suggestion="Verify crude quality. Unusual API gravity may indicate contamination.",
                value=entry.api_gravity
            ))

        return issues

    async def _detect_anomalies(self, entry: ProductionEntry) -> List[ValidationIssue]:
        """Detect statistical anomalies using historical data"""
        issues = []

        try:
            # Fetch historical data for this partner (last 30 days)
            historical_entries = firestore_client.query_documents(
                collection=config.COLLECTION_PRODUCTION_ENTRIES,
                filters=[
                    ('partner', '==', entry.partner),
                    ('flagged', '==', False)  # Only use validated data
                ],
                order_by='timestamp',
                limit=30
            )

            if len(historical_entries) < config.MIN_HISTORICAL_SAMPLES:
                logger.info(f"Insufficient historical data for {entry.partner}")
                return issues

            # Extract volumes
            volumes = [e['gross_volume_bbl'] for e in historical_entries]

            # Calculate z-score
            mean = statistics.mean(volumes)
            if len(volumes) > 1:
                stdev = statistics.stdev(volumes)
                z_score = (entry.gross_volume_bbl - mean) / stdev if stdev > 0 else 0

                if abs(z_score) > config.Z_SCORE_THRESHOLD:
                    issues.append(ValidationIssue(
                        field="gross_volume_bbl",
                        severity=SeverityLevel.MEDIUM,
                        message=f"Volume {entry.gross_volume_bbl} bbl is {abs(z_score):.2f} standard deviations from average",
                        suggestion=f"Historical average: {mean:.2f} bbl. Verify meter reading.",
                        value=entry.gross_volume_bbl
                    ))

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")

        return issues

    def _determine_status(self, issues: List[ValidationIssue]) -> Tuple[ValidationStatus, bool]:
        """Determine validation status based on issues"""
        high_severity_count = len([i for i in issues if i.severity == SeverityLevel.HIGH])

        if high_severity_count > 0:
            return ValidationStatus.FLAGGED, True
        elif len(issues) > 0:
            return ValidationStatus.WARNING, False
        else:
            return ValidationStatus.VALID, False

    def _calculate_confidence(self, issues: List[ValidationIssue]) -> float:
        """Calculate confidence score (0-100)"""
        if not issues:
            return 100.0

        severity_weights = {
            SeverityLevel.LOW: 5,
            SeverityLevel.MEDIUM: 15,
            SeverityLevel.HIGH: 30
        }

        total_deduction = sum(severity_weights.get(issue.severity, 10) for issue in issues)
        return max(0.0, 100.0 - total_deduction)

    def _update_firestore(self, entry_id: str, result: ValidationResult) -> None:
        """Update production entry in Firestore"""
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
        """Log agent activity"""
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
            'execution_time_ms': execution_time,
            'timestamp': datetime.utcnow().isoformat()
        }

        firestore_client.log_agent_activity(log_data)


# Singleton instance
auditor_agent = AuditorAgent()
