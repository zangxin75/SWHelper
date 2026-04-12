# 对应需求文件: 文档/需求/req_tool_wrapper.md

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Python脚本')))

from tool_wrapper import ToolWrapper


# Test cases for tool calls
TOOL_CALL_TEST_CASES = [
    # T-01: Initialize with mock mode
    {
        "id": "T-01",
        "description": "Initialize with mock mode",
        "init_kwargs": {"use_mock": True},
        "expected_adapter_type": "MockAdapter"
    },
    # T-02: Initialize with real mode
    {
        "id": "T-02",
        "description": "Initialize with real mode",
        "init_kwargs": {"use_mock": False},
        "expected_adapter_type": "SWAdapter"
    },
]


@pytest.fixture
def mock_adapter():
    """Create a mock adapter."""
    adapter = Mock()
    adapter.is_available = AsyncMock(return_value=True)
    adapter.call_tool = AsyncMock(return_value={"success": True, "result": {"part_id": "test-part-123"}})
    adapter.list_tools = AsyncMock(return_value=["create_part", "create_sketch", "extrude"])
    return adapter


@pytest.fixture
def tool_wrapper_with_mock(mock_adapter):
    """Create a ToolWrapper with a mock adapter."""
    with patch('tool_wrapper.SWAdapter', return_value=mock_adapter):
        wrapper = ToolWrapper(use_mock=True)
        wrapper._adapter = mock_adapter
        return wrapper


class TestToolWrapperInit:
    """Test ToolWrapper initialization."""

    @pytest.mark.asyncio
    async def test_init_mock_mode(self):
        """T-01: Initialize with mock mode."""
        wrapper = ToolWrapper(use_mock=True)
        assert wrapper is not None
        assert wrapper._adapter is not None

    @pytest.mark.asyncio
    async def test_init_real_mode(self):
        """T-02: Initialize with real mode."""
        with patch('tool_wrapper.SWAdapter') as mock_sw_adapter:
            wrapper = ToolWrapper(use_mock=False)
            assert wrapper is not None

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        wrapper = ToolWrapper(use_mock=True, timeout=30)
        assert wrapper._timeout == 30

    def test_init_custom_retries(self):
        """Test initialization with custom max retries."""
        wrapper = ToolWrapper(use_mock=True, max_retries=5)
        assert wrapper._max_retries == 5


class TestToolWrapperCall:
    """Test tool call functionality."""

    @pytest.mark.asyncio
    async def test_call_existing_tool(self, tool_wrapper_with_mock):
        """T-03: Call an existing tool successfully."""
        result = await tool_wrapper_with_mock.call_tool(
            "create_part",
            {"template": "part"}
        )
        assert result["success"] is True
        assert "result" in result

    @pytest.mark.asyncio
    async def test_call_nonexistent_tool(self, tool_wrapper_with_mock):
        """T-04: Call a non-existent tool."""
        # Mock the tool list to not include unknown_tool
        tool_wrapper_with_mock._adapter.list_tools = AsyncMock(return_value=["create_part"])

        result = await tool_wrapper_with_mock.call_tool(
            "unknown_tool",
            {}
        )
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_call_tool_timeout(self):
        """T-06: Tool call timeout handling."""
        # Create a wrapper with very short timeout
        wrapper = ToolWrapper(use_mock=True, timeout=0.1)

        # Mock adapter that takes too long
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(2)
            return {"success": True}

        wrapper._adapter.call_tool = AsyncMock(side_effect=slow_call)
        # Also need to mock list_tools to include the tool we're testing
        wrapper._adapter.list_tools = AsyncMock(return_value=["create_part"])

        result = await wrapper.call_tool("create_part", {})
        assert result["success"] is False
        assert "timed out" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_call_tool_with_retries(self):
        """T-07: Tool call with automatic retry."""
        wrapper = ToolWrapper(use_mock=True, max_retries=3)

        # Mock adapter that fails twice then succeeds
        call_count = 0

        async def flaky_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"success": True, "result": {"data": "success"}}

        wrapper._adapter.call_tool = AsyncMock(side_effect=flaky_call)
        # Also need to mock list_tools to include the tool we're testing
        wrapper._adapter.list_tools = AsyncMock(return_value=["create_part"])

        result = await wrapper.call_tool("create_part", {})
        assert result["success"] is True
        assert call_count == 3  # Failed twice, succeeded on third try

    @pytest.mark.asyncio
    async def test_call_tool_invalid_params(self, tool_wrapper_with_mock):
        """T-08: Parameter validation failure."""
        result = await tool_wrapper_with_mock.call_tool(
            "create_part",
            None
        )
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_call_tool_exception_in_adapter(self, tool_wrapper_with_mock):
        """Test handling exception raised by adapter."""
        tool_wrapper_with_mock._adapter.call_tool = AsyncMock(
            side_effect=Exception("Adapter error")
        )

        result = await tool_wrapper_with_mock.call_tool("create_part", {})
        assert result["success"] is False
        assert "error" in result


class TestToolWrapperList:
    """Test tool listing functionality."""

    @pytest.mark.asyncio
    async def test_list_tools(self, tool_wrapper_with_mock):
        """T-05: List all available tools."""
        tools = await tool_wrapper_with_mock.list_tools()
        assert len(tools) > 0
        assert "create_part" in tools

    @pytest.mark.asyncio
    async def test_list_tools_empty(self):
        """Test listing tools when none available."""
        wrapper = ToolWrapper(use_mock=True)
        wrapper._adapter.list_tools = AsyncMock(return_value=[])

        tools = await wrapper.list_tools()
        assert tools == []

    @pytest.mark.asyncio
    async def test_list_tools_error_handling(self, tool_wrapper_with_mock):
        """Test error handling in list_tools."""
        tool_wrapper_with_mock._adapter.list_tools = AsyncMock(
            side_effect=Exception("List error")
        )

        tools = await tool_wrapper_with_mock.list_tools()
        assert tools == []


class TestToolWrapperBehavior:
    """Test additional ToolWrapper behaviors."""

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries is exceeded."""
        wrapper = ToolWrapper(use_mock=True, max_retries=2)

        # Mock adapter that always fails
        wrapper._adapter.call_tool = AsyncMock(
            side_effect=Exception("Persistent failure")
        )

        result = await wrapper.call_tool("failing_tool", {})
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, tool_wrapper_with_mock):
        """Test concurrent tool calls."""
        tool_wrapper_with_mock._adapter.call_tool = AsyncMock(
            return_value={"success": True, "result": {"id": "test"}}
        )

        # Make multiple concurrent calls
        results = await asyncio.gather(
            tool_wrapper_with_mock.call_tool("create_part", {"name": "part1"}),
            tool_wrapper_with_mock.call_tool("create_part", {"name": "part2"}),
            tool_wrapper_with_mock.call_tool("create_part", {"name": "part3"}),
        )

        assert all(r["success"] for r in results)
        assert tool_wrapper_with_mock._adapter.call_tool.call_count == 3

    @pytest.mark.asyncio
    async def test_tool_caching(self, tool_wrapper_with_mock):
        """Test that tool list is cached appropriately."""
        # Call list_tools multiple times
        tools1 = await tool_wrapper_with_mock.list_tools()
        tools2 = await tool_wrapper_with_mock.list_tools()

        assert tools1 == tools2
