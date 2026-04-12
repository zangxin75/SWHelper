"""
Test knowledge_base module.

Corresponding requirements file: 文档/需求/req_knowledge_base.md
"""
import pytest
from typing import Dict, Any, List, Optional


# Will import from knowledge_base once implemented
# from knowledge_base import KnowledgeBase


# Material test cases (K-01 to K-05)
MATERIAL_TEST_CASES = [
    # K-01: Query known material - Aluminum 6061
    (
        "铝合金_6061",
        {
            "density": 2.7,
            "yield_strength": 276,
            "typical_uses": ["机架", "支架", "外壳"]
        }
    ),
    # K-02: Query known material - Stainless Steel 304
    (
        "不锈钢_304",
        {
            "density": 7.93,
            "yield_strength": 290,
            "typical_uses": ["管道", "食品设备", "化工"]
        }
    ),
    # K-03: Query known material - Carbon Steel Q235
    (
        "碳钢_Q235",
        {
            "density": 7.85,
            "yield_strength": 235,
            "typical_uses": ["结构件", "机械零件"]
        }
    ),
    # K-04: Query non-existent material
    (
        "未知材料_XYZ",
        None
    ),
    # K-05: Empty string query
    (
        "",
        None
    ),
]


# Design rule test cases (K-06 to K-09)
DESIGN_RULE_TEST_CASES = [
    # K-06: Get design rule - minimum wall thickness
    (
        "最小壁厚",
        "根据零件尺寸和材料决定"
    ),
    # K-07: Get design rule - draft angle
    (
        "拔模角度",
        "通常 1-3 度"
    ),
    # K-08: Get design rule - fillet radius
    (
        "圆角半径",
        "最小为壁厚的 25%"
    ),
    # K-09: Get non-existent design rule
    (
        "未知规则",
        None
    ),
]


# Standard component test cases (K-10 to K-12)
STANDARD_COMPONENT_TEST_CASES = [
    # K-10: Query standard component - M6 bolt
    (
        {"type": "螺栓", "size": "M6"},
        {
            "name": "M6螺栓",
            "pitch": 1.0,
            "length_range": [10, 100]
        }
    ),
    # K-11: Query standard component - 6200 bearing
    (
        {"type": "轴承", "size": "6200"},
        {
            "name": "6200轴承",
            "bore": 10,
            "od": 30,
            "width": 9
        }
    ),
    # K-12: Query non-existent standard component
    (
        {"type": "未知", "size": "XXX"},
        None
    ),
]


class TestKnowledgeBaseMaterials:
    """Test material query functionality."""

    @pytest.mark.parametrize(
        "material_name,expected",
        MATERIAL_TEST_CASES,
        ids=["K-01", "K-02", "K-03", "K-04", "K-05"]
    )
    def test_get_material(
        self,
        material_name: str,
        expected: Optional[Dict[str, Any]]
    ):
        """Test retrieving material properties by name."""
        # Import here to avoid import errors before implementation
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.get_material(material_name)

        assert result == expected

    def test_material_returns_dict_with_correct_keys(self):
        """Test that material data contains expected keys."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.get_material("铝合金_6061")

        assert result is not None
        assert "density" in result
        assert "yield_strength" in result
        assert "typical_uses" in result
        assert isinstance(result["density"], (int, float))
        assert isinstance(result["yield_strength"], (int, float))
        assert isinstance(result["typical_uses"], list)


class TestKnowledgeBaseDesignRules:
    """Test design rule query functionality."""

    @pytest.mark.parametrize(
        "rule_name,expected",
        DESIGN_RULE_TEST_CASES,
        ids=["K-06", "K-07", "K-08", "K-09"]
    )
    def test_get_design_rule(
        self,
        rule_name: str,
        expected: Optional[str]
    ):
        """Test retrieving design rules by name."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.get_design_rule(rule_name)

        assert result == expected

    def test_design_rule_returns_string_or_none(self):
        """Test that design rules are strings or None."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.get_design_rule("最小壁厚")

        assert result is None or isinstance(result, str)

    def test_get_design_rule_with_empty_string(self):
        """Test getting design rule with empty string."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.get_design_rule("")

        assert result is None


class TestKnowledgeBaseStandardComponents:
    """Test standard component query functionality."""

    @pytest.mark.parametrize(
        "query,expected",
        STANDARD_COMPONENT_TEST_CASES,
        ids=["K-10", "K-11", "K-12"]
    )
    def test_search_standard_component(
        self,
        query: Dict[str, str],
        expected: Optional[Dict[str, Any]]
    ):
        """Test searching for standard components."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.search_standard_component(query["type"], query.get("size"))

        assert result == expected

    def test_standard_component_returns_dict_with_correct_keys(self):
        """Test that standard component data contains expected keys."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.search_standard_component("螺栓", "M6")

        assert result is not None
        assert "name" in result
        assert isinstance(result["name"], str)

    def test_search_standard_component_with_empty_type(self):
        """Test searching with empty component type."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.search_standard_component("")

        assert result is None

    def test_search_standard_component_without_size(self):
        """Test searching without size parameter (returns first match)."""
        from knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        result = kb.search_standard_component("螺栓")

        assert result is not None
        assert "name" in result
