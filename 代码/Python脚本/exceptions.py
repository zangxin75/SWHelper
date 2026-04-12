"""
Custom exception hierarchy for Agent error handling
"""


class AgentError(Exception):
    """Base exception for all Agent errors"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class IntentUnderstandingError(AgentError):
    """Error during intent understanding phase"""
    pass


class TaskDecompositionError(AgentError):
    """Error during task decomposition phase"""
    pass


class ToolExecutionError(AgentError):
    """Error during tool execution"""

    def __init__(self, tool_name: str, message: str, details: dict = None):
        self.tool_name = tool_name
        super().__init__(message, details)


class ValidationError(AgentError):
    """Error during validation phase"""
    pass


class ConfigurationError(AgentError):
    """Error in configuration"""
    pass
