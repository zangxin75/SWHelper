"""
Interface definitions for dependency injection and testability
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from schemas import Intent, Task, ToolResult, ExecutionResult, ValidationReport


class IKnowledgeBase(ABC):
    """Knowledge base interface for materials, rules, standards"""

    @abstractmethod
    def get_material(self, name: str) -> Dict[str, Any]:
        """Get material properties by name"""
        pass

    @abstractmethod
    def get_design_rules(self, category: str) -> Dict[str, Any]:
        """Get design rules by category"""
        pass


class IIntentUnderstanding(ABC):
    """Intent understanding interface for NLU"""

    @abstractmethod
    async def understand(self, user_input: str) -> Intent:
        """Understand user intent from natural language"""
        pass


class ITaskDecomposer(ABC):
    """Task decomposition interface for breaking down intents"""

    @abstractmethod
    async def decompose(self, intent: Intent) -> List[Task]:
        """Decompose intent into executable task sequence"""
        pass


class IToolWrapper(ABC):
    """Tool wrapper interface for MCP tool invocation"""

    @abstractmethod
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Call a specific MCP tool"""
        pass

    @abstractmethod
    def list_tools(self) -> List[str]:
        """List all available tools"""
        pass


class ITaskExecutor(ABC):
    """Task executor interface for running task sequences"""

    @abstractmethod
    async def execute(self, tasks: List[Task]) -> ExecutionResult:
        """Execute a sequence of tasks with dependency handling"""
        pass


class IResultValidator(ABC):
    """Result validator interface for design verification"""

    @abstractmethod
    async def validate(self, results: List[ToolResult], intent: Intent) -> ValidationReport:
        """Validate execution results against intent"""
        pass
