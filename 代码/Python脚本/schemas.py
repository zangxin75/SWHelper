"""
Pydantic data models for type safety and validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class ActionType(str, Enum):
    """Action types for intent understanding"""
    CREATE = "create"
    MODIFY = "modify"
    ANALYZE = "analyze"
    EXPORT = "export"
    UNKNOWN = "unknown"  # For unparseable inputs


class ObjectType(str, Enum):
    """Object types for intent understanding"""
    PART = "part"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"
    FEATURE = "feature"  # For features that require existing model
    UNKNOWN = "unknown"  # For unrecognizable objects


class Intent(BaseModel):
    """Structured intent from natural language understanding"""
    action: ActionType
    object: ObjectType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_input: str


class Task(BaseModel):
    """Executable task with dependencies"""
    id: str
    tool: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str


class ExecutionResult(BaseModel):
    """Result from executing a task sequence"""
    results: List[ToolResult]
    failed_tasks: List[str] = Field(default_factory=list)
    total_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0


class ValidationIssue(BaseModel):
    """Validation issue or warning"""
    severity: str  # "error" or "warning"
    message: str
    location: Optional[str] = None


class ValidationReport(BaseModel):
    """Validation report for design results"""
    passed: bool
    issues: List[ValidationIssue] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)


class CoordinatorResult(BaseModel):
    """Final result from coordinator"""
    success: bool
    intent: Intent
    tasks: List[Task]
    execution: ExecutionResult
    validation: ValidationReport
    user_feedback: str
    total_time: float
