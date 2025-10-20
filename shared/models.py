"""
Pydantic models for data validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ValidationStatus(str, Enum):
    VALID = "valid"
    WARNING = "warning"
    FLAGGED = "flagged"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class ProductionEntry(BaseModel):
    """Production entry data model"""
    id: Optional[str] = None
    partner: str
    gross_volume_bbl: float
    bsw_percent: float
    temperature_degF: float
    api_gravity: float
    timestamp: str
    created_at: Optional[str] = None

    # Validation fields (added by Auditor)
    flagged: Optional[bool] = False
    validation_status: Optional[ValidationStatus] = None
    ai_reason: Optional[str] = None
    confidence_score: Optional[float] = None

    @field_validator('gross_volume_bbl')
    @classmethod
    def volume_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Gross volume must be positive')
        return v


class ValidationIssue(BaseModel):
    """Validation issue found by Auditor"""
    field: str
    severity: SeverityLevel
    message: str
    suggestion: str
    value: Any


class ValidationResult(BaseModel):
    """Result from Auditor Agent"""
    entry_id: str
    status: ValidationStatus
    flagged: bool
    issues: List[ValidationIssue]
    ai_analysis: str
    confidence_score: float
    timestamp: str


class TerminalReceipt(BaseModel):
    """Terminal receipt data model"""
    id: Optional[str] = None
    terminal_name: str
    total_volume_bbl: float
    receipt_date: str
    meter_reading: Optional[float] = None
    ticket_number: Optional[str] = None
    created_at: Optional[str] = None


class PartnerAllocation(BaseModel):
    """Allocation for a single partner"""
    partner: str
    share_percentage: float
    gross_volume: float
    temperature_correction: float = 0.0
    bsw_deduction: float
    shrinkage_deduction: float
    net_volume: float
    allocated_volume: float
    entries_count: Optional[int] = 0


class AllocationResult(BaseModel):
    """Result from Accountant Agent"""
    receipt_id: str
    allocations: List[Dict[str, Any]]  # List of allocation dictionaries
    total_allocated: float
    validation_status: bool = True
    timestamp: str


class ReconciliationRun(BaseModel):
    """Reconciliation run result"""
    id: Optional[str] = None
    terminal_receipt_id: str
    start_date: str
    end_date: str
    total_production: float
    total_terminal_volume: float
    variance: float
    variance_percentage: float
    partner_allocations: List[PartnerAllocation]
    status: str = "pending_review"
    created_at: Optional[str] = None


class Notification(BaseModel):
    """Notification for stakeholders (Communicator Agent)"""
    id: Optional[str] = None
    type: NotificationType  # email, sms, webhook
    recipient: Union[str, List[str]]  # email address(es), phone number, or webhook URL - supports batch emails
    subject: Optional[str] = None  # for email
    body: str  # message content or payload
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # additional data (cc, bcc, headers, etc.)
    created_at: Optional[str] = None


class AgentLog(BaseModel):
    """Log entry for agent activity"""
    agent_name: str
    action: str
    status: str  # "started", "completed", "failed"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
