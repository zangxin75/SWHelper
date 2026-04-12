"""
Knowledge Base module for SolidWorks design automation.

Provides access to materials, design rules, and standard components.
"""
from typing import Dict, Any, List, Optional


class KnowledgeBase:
    """
    Knowledge base for SolidWorks design automation.

    Provides access to:
    - Material properties (density, yield strength, typical uses)
    - Design rules (wall thickness, draft angles, fillet radii)
    - Standard components (bolts, bearings, etc.)
    """

    def __init__(self):
        """Initialize the knowledge base with pre-populated data."""
        # Material database
        self._materials: Dict[str, Dict[str, Any]] = {
            "铝合金_6061": {
                "density": 2.7,
                "yield_strength": 276,
                "typical_uses": ["机架", "支架", "外壳"]
            },
            "不锈钢_304": {
                "density": 7.93,
                "yield_strength": 290,
                "typical_uses": ["管道", "食品设备", "化工"]
            },
            "碳钢_Q235": {
                "density": 7.85,
                "yield_strength": 235,
                "typical_uses": ["结构件", "机械零件"]
            }
        }

        # Design rules database
        self._design_rules: Dict[str, str] = {
            "最小壁厚": "根据零件尺寸和材料决定",
            "拔模角度": "通常 1-3 度",
            "圆角半径": "最小为壁厚的 25%"
        }

        # Standard components database
        self._standard_components: Dict[str, Dict[str, Dict[str, Any]]] = {
            "螺栓": {
                "M6": {
                    "name": "M6螺栓",
                    "pitch": 1.0,
                    "length_range": [10, 100]
                }
            },
            "轴承": {
                "6200": {
                    "name": "6200轴承",
                    "bore": 10,
                    "od": 30,
                    "width": 9
                }
            }
        }

    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        Get material properties by name.

        Args:
            material_name: Name of the material (e.g., "铝合金_6061")

        Returns:
            Dictionary with material properties (density, yield_strength, typical_uses)
            or None if material not found

        Examples:
            >>> kb = KnowledgeBase()
            >>> material = kb.get_material("铝合金_6061")
            >>> material["density"]
            2.7
        """
        if not material_name:
            return None

        return self._materials.get(material_name)

    def get_design_rule(self, rule_name: str) -> Optional[str]:
        """
        Get design rule by name.

        Args:
            rule_name: Name of the design rule (e.g., "最小壁厚")

        Returns:
            Design rule description as string, or None if rule not found

        Examples:
            >>> kb = KnowledgeBase()
            >>> rule = kb.get_design_rule("拔模角度")
            >>> rule
            '通常 1-3 度'
        """
        if not rule_name:
            return None

        return self._design_rules.get(rule_name)

    def search_standard_component(
        self,
        component_type: str,
        size: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for standard components by type and size.

        Args:
            component_type: Type of component (e.g., "螺栓", "轴承")
            size: Size specification (e.g., "M6", "6200"). If None, returns first match.

        Returns:
            Dictionary with component specifications, or None if not found

        Examples:
            >>> kb = KnowledgeBase()
            >>> bolt = kb.search_standard_component("螺栓", "M6")
            >>> bolt["name"]
            'M6螺栓'
        """
        if not component_type:
            return None

        type_dict = self._standard_components.get(component_type)
        if not type_dict:
            return None

        if size is None:
            # Return first available component of this type
            return next(iter(type_dict.values()), None)

        return type_dict.get(size)
