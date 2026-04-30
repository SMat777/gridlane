"""
Structured error system for the Gridlane engine.

Every API error uses ErrorCode + ErrorResponse so the frontend
can show context-specific messages instead of raw strings.

Usage in endpoints:
    raise PipelineError(ErrorCode.CYCLE_DETECTED, "Pipeline has a cycle")

The global exception handler converts these to structured JSON responses.
"""

from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
    """Machine-readable error codes.

    Frontend maps these to user-friendly messages.
    Add new codes as connectors introduce new failure modes.
    """

    # Pipeline validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    ORPHAN_EDGE = "ORPHAN_EDGE"
    CONFIG_INVALID = "CONFIG_INVALID"

    # Execution
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    EXECUTOR_FAILED = "EXECUTOR_FAILED"
    UNKNOWN_NODE_TYPE = "UNKNOWN_NODE_TYPE"

    # Connectors (added as connectors are built)
    CONNECTOR_AUTH_FAILED = "CONNECTOR_AUTH_FAILED"
    CONNECTOR_NETWORK_ERROR = "CONNECTOR_NETWORK_ERROR"
    CONNECTOR_TIMEOUT = "CONNECTOR_TIMEOUT"
    CONNECTOR_RATE_LIMITED = "CONNECTOR_RATE_LIMITED"

    # General
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """Structured error response body.

    Always includes code + message. Details is optional context
    that the frontend can use for inline validation errors, etc.
    """

    code: ErrorCode
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """API error response wrapper."""

    error: ErrorDetail


class PipelineError(Exception):
    """Structured exception that maps to an HTTP error response.

    Raise this in endpoints/services instead of HTTPException
    when you want structured error codes in the response body.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)
