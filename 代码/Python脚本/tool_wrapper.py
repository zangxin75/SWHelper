"""
Tool Wrapper Module

Provides a unified interface to call SolidWorks MCP tools.
Handles retries, timeouts, and error recovery.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

# Try to import MCP adapter, fallback to mock if not available
try:
    from sw_mcp_adapter import SWAdapter
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    SWAdapter = None


logger = logging.getLogger(__name__)


class ToolWrapper:
    """
    Wrapper for SolidWorks MCP tools.

    Provides a unified interface with retry logic, timeout handling,
    and error recovery for all 106 MCP tools.
    """

    def __init__(
        self,
        use_mock: bool = False,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the tool wrapper.

        Args:
            use_mock: If True, use mock adapter for testing
            timeout: Timeout in seconds for tool calls
            max_retries: Maximum number of retry attempts
        """
        self._timeout = timeout
        self._max_retries = max_retries
        self._tool_list: Optional[List[str]] = None

        if use_mock or not MCP_AVAILABLE:
            # Use mock adapter for testing or when MCP is not available
            self._adapter = MockAdapter()
            logger.info("ToolWrapper initialized with mock adapter")
        else:
            # Use real MCP adapter
            self._adapter = SWAdapter()
            logger.info("ToolWrapper initialized with real MCP adapter")

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a SolidWorks MCP tool.

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool

        Returns:
            Dictionary with success status and result or error
        """
        # Validate parameters
        if parameters is None:
            return {
                "success": False,
                "error": "Invalid parameters: parameters cannot be None"
            }

        # Check if tool exists
        available_tools = await self.list_tools()
        if tool_name not in available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {', '.join(available_tools)}"
            }

        # Try calling the tool with retry logic
        last_error = None
        for attempt in range(self._max_retries):
            try:
                # Call with timeout
                result = await asyncio.wait_for(
                    self._adapter.call_tool(tool_name, parameters),
                    timeout=self._timeout
                )

                logger.info(f"Tool '{tool_name}' called successfully on attempt {attempt + 1}")
                return {
                    "success": True,
                    "result": result
                }

            except asyncio.TimeoutError:
                last_error = f"Tool call timed out after {self._timeout} seconds"
                logger.warning(f"Tool '{tool_name}' timed out on attempt {attempt + 1}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool '{tool_name}' failed on attempt {attempt + 1}: {e}")

            # Wait before retry (exponential backoff)
            if attempt < self._max_retries - 1:
                await asyncio.sleep(2 ** attempt)

        # All retries exhausted
        return {
            "success": False,
            "error": last_error or "Max retries exceeded"
        }

    async def list_tools(self) -> List[str]:
        """
        List all available SolidWorks MCP tools.

        Returns:
            List of tool names
        """
        try:
            if self._tool_list is None:
                # Load tool list
                self._tool_list = await self._load_tool_list()
            return self._tool_list
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    async def _load_tool_list(self) -> List[str]:
        """
        Load the list of available tools from the adapter.

        Returns:
            List of tool names
        """
        try:
            tools = await self._adapter.list_tools()
            return tools
        except Exception as e:
            logger.error(f"Failed to load tool list: {e}")
            return []


class MockAdapter:
    """
    Mock adapter for testing purposes.

    Simulates the SolidWorks MCP adapter without requiring
    the actual SolidWorks application.
    """

    def __init__(self):
        """Initialize mock adapter with simulated tools."""
        self._tools = [
            "create_part",
            "create_sketch",
            "extrude",
            "revolve",
            "fillet",
            "chamfer",
            "pattern_linear",
            "pattern_circular",
            "assembly_insert_component",
            "assembly_mate",
            "drawing_create_view",
            "dimension_add",
        ]
        self._call_count = {}

    async def is_available(self) -> bool:
        """Check if the mock adapter is available."""
        return True

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate calling a tool.

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool

        Returns:
            Mock result
        """
        # Track call count
        self._call_count[tool_name] = self._call_count.get(tool_name, 0) + 1

        # Simulate tool-specific behavior
        if tool_name == "create_part":
            return {
                "part_id": f"mock-part-{self._call_count[tool_name]}",
                "template": parameters.get("template", "default"),
                "status": "created"
            }
        elif tool_name == "create_sketch":
            return {
                "sketch_id": f"mock-sketch-{self._call_count[tool_name]}",
                "plane": parameters.get("plane", "front"),
                "status": "created"
            }
        elif tool_name == "extrude":
            return {
                "feature_id": f"mock-extrude-{self._call_count[tool_name]}",
                "depth": parameters.get("depth", 10),
                "status": "extruded"
            }
        else:
            # Generic response for other tools
            return {
                "tool": tool_name,
                "call_count": self._call_count[tool_name],
                "status": "executed"
            }

    async def list_tools(self) -> List[str]:
        """Return list of available mock tools."""
        return self._tools.copy()
