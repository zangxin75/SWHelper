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

        # Standard components database (FIX-05: 扩展标准件数据库)
        self._standard_components: Dict[str, Dict[str, Dict[str, Any]]] = {
            "螺栓": {
                "M6": {
                    "name": "M6螺栓",
                    "pitch": 1.0,
                    "length_range": [10, 100],
                    "head_diameter": 10,
                    "thread_diameter": 6
                },
                "M8": {
                    "name": "M8螺栓",
                    "pitch": 1.25,
                    "length_range": [12, 120],
                    "head_diameter": 13,
                    "thread_diameter": 8
                },
                "M10": {
                    "name": "M10螺栓",
                    "pitch": 1.5,
                    "length_range": [16, 150],
                    "head_diameter": 16,
                    "thread_diameter": 10
                },
                "M12": {
                    "name": "M12螺栓",
                    "pitch": 1.75,
                    "length_range": [20, 180],
                    "head_diameter": 18,
                    "thread_diameter": 12
                }
            },
            "螺母": {
                "M6": {
                    "name": "M6螺母",
                    "pitch": 1.0,
                    "thickness": 5,
                    "width": 10
                },
                "M8": {
                    "name": "M8螺母",
                    "pitch": 1.25,
                    "thickness": 6.5,
                    "width": 13
                },
                "M10": {
                    "name": "M10螺母",
                    "pitch": 1.5,
                    "thickness": 8,
                    "width": 16
                },
                "M12": {
                    "name": "M12螺母",
                    "pitch": 1.75,
                    "thickness": 10,
                    "width": 18
                }
            },
            "轴承": {
                "6200": {
                    "name": "6200轴承",
                    "bore": 10,
                    "od": 30,
                    "width": 9
                },
                "6201": {
                    "name": "6201轴承",
                    "bore": 12,
                    "od": 32,
                    "width": 10
                },
                "6202": {
                    "name": "6202轴承",
                    "bore": 15,
                    "od": 35,
                    "width": 11
                },
                "6300": {
                    "name": "6300轴承",
                    "bore": 10,
                    "od": 35,
                    "width": 11
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
        user_input: str,
        size: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for standard components (FIX-05: 支持自然语言输入).

        Args:
            user_input: User input string (e.g., "M10x20螺栓", "螺栓", "M6轴承")
            size: Legacy parameter (for backward compatibility). If user_input is a component_type,
                  this parameter specifies the size.

        Returns:
            Dictionary with component specifications, or None if not found

        Examples:
            >>> kb = KnowledgeBase()
            >>> bolt = kb.search_standard_component("M10x20螺栓")
            >>> bolt["name"]
            'M10螺栓'
            >>> nut = kb.search_standard_component("M8螺母")
            >>> nut["name"]
            'M8螺母'
        """
        import re

        if not user_input:
            return None

        # 解析自然语言输入，提取component_type和size
        # 支持格式: "M10x20螺栓", "M6螺栓", "螺栓"
        component_type = None
        size_spec = None

        # 提取类型（螺栓、螺母、轴承等）
        for type_name in self._standard_components.keys():
            if type_name in user_input:
                component_type = type_name
                break

        if not component_type:
            # 如果没有找到类型，返回None
            return None

        # 提取尺寸规格（M6, M8, M10, M12, 6200, 6201, 6300等）
        # 匹配螺栓/螺母: M6, M8, M10, M12
        bolt_match = re.search(r'M\d+(?:\.\d+)?', user_input, re.IGNORECASE)
        if bolt_match:
            size_spec = bolt_match.group(0).upper()
        else:
            # 匹配轴承: 6200, 6201, 6300等（4位数字）
            bearing_match = re.search(r'\d{4}', user_input)
            if bearing_match:
                size_spec = bearing_match.group(0)

        # 如果用户只提供了类型（如"螺栓"），返回第一个匹配项
        if not size_spec:
            type_dict = self._standard_components.get(component_type)
            if not type_dict:
                return None
            return next(iter(type_dict.values()), None)

        # 查找具体的标准件
        type_dict = self._standard_components.get(component_type)
        if not type_dict:
            return None

        component = type_dict.get(size_spec)
        if component:
            # 添加解析信息到返回结果
            result = component.copy()
            result["type"] = component_type
            result["specification"] = size_spec
            return result

        return None
