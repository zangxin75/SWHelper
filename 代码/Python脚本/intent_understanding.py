"""
意图理解模块

功能: 将自然语言输入解析为结构化意图
支持两种模式:
1. Claude API模式: 使用Claude API进行高级意图理解
2. 本地模式: 基于规则的NLU (正则表达式匹配)

需求文件: 文档/需求/req_intent_understanding.md
"""

import re
import json
from enum import Enum
from typing import Optional, Dict, Any, List


class IntentAction(Enum):
    """意图动作枚举"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    ANALYZE = "analyze"
    EXPORT = "export"
    IMPORT = "import"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"


class IntentObject(Enum):
    """意图对象枚举"""
    PART = "part"
    ASSEMBLY = "assembly"
    DRAWING = "drawing"
    FEATURE = "feature"
    SKETCH = "sketch"


class IntentUnderstanding:
    """
    意图理解类

    支持两种模式:
    1. Claude API模式: 使用Claude API进行高级理解
    2. 本地模式: 基于规则的匹配 (正则表达式)

    自动降级: Claude API失败时自动切换到本地模式
    """

    def __init__(self, use_claude: bool = False, api_key: Optional[str] = None):
        """
        初始化意图理解模块

        Args:
            use_claude: 是否使用Claude API
            api_key: Claude API密钥 (use_claude=True时需要)
        """
        self.use_claude = use_claude
        self.api_key = api_key
        self.claude_client = None

        # 尝试初始化Claude客户端
        if self.use_claude:
            self._init_claude_client()

        # 编译正则表达式模式
        self._compile_patterns()

    def _init_claude_client(self):
        """初始化Claude API客户端"""
        try:
            import anthropic
            if self.api_key:
                self.claude_client = anthropic.Anthropic(api_key=self.api_key)
            else:
                # 尝试从环境变量获取
                self.claude_client = anthropic.Anthropic()
        except ImportError:
            print("Warning: anthropic package not installed, falling back to local mode")
            self.use_claude = False
            self.claude_client = None
        except Exception as e:
            print(f"Warning: Failed to initialize Claude client: {e}, falling back to local mode")
            self.use_claude = False
            self.claude_client = None

    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 动作关键词模式
        self.action_patterns = {
            IntentAction.CREATE: [
                r'创建|生成|新建|增加|添加|画|绘制|make|create|add|draw',
                r'做一个?|做一个?.+',
            ],
            IntentAction.MODIFY: [
                r'修改|改变|调整|更新|编辑|设置|modify|change|edit|update|set',
            ],
            IntentAction.DELETE: [
                r'删除|移除|清除|去掉|delete|remove|clear',
            ],
            IntentAction.ANALYZE: [
                r'分析|计算|测量|检查|评估|analyze|calculate|measure|check',
            ],
            IntentAction.EXPORT: [
                r'导出|保存|输出|export|save|output',
            ],
            IntentAction.IMPORT: [
                r'导入|打开|加载|import|open|load',
            ],
            IntentAction.ASSEMBLY: [
                r'装配|组装|配合|assembly|mate|assemble',
            ],
            IntentAction.DRAWING: [
                r'工程图|图纸|drawing|draft',
            ],
        }

        # 对象关键词模式
        self.object_patterns = {
            IntentObject.PART: [
                r'零件|部件|实体|方块|圆柱|球体|part|component|solid|body',
                r'方块|圆柱|球体|立方体|长方体',
            ],
            IntentObject.ASSEMBLY: [
                r'装配|组件|产品|assembly|assembly',
            ],
            IntentObject.DRAWING: [
                r'工程图|视图|图纸|drawing|view|draft',
            ],
            IntentObject.FEATURE: [
                r'特征|拉伸|旋转|扫描|放样|feature|extrude|revolve|sweep|loft',
                r'孔|倒角|圆角|fillet|chamfer|hole',
            ],
            IntentObject.SKETCH: [
                r'草图|sketch',
            ],
        }

        # 尺寸提取模式
        self.dimension_patterns = [
            # 匹配 100x100x50, 100*100*50, 100X100X50
            r'(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)',
            # 匹配 "尺寸为100x100x50"
            r'尺寸为\s*(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)',
            # 匹配 "100mm x 100mm x 50mm"
            r'(\d+(?:\.\d+)?)\s*mm\s*[xX*]\s*(\d+(?:\.\d+)?)\s*mm\s*[xX*]\s*(\d+(?:\.\d+)?)\s*mm',
        ]

        # 材料提取模式
        self.material_patterns = [
            (r'铝合金|铝材|铝', '铝合金_6061'),
            (r'钢|钢材', '钢_普通'),
            (r'不锈钢', '不锈钢_304'),
            (r'铁|铸铁', '铁_铸铁'),
            (r'塑料|ABS塑料|ABS', 'ABS塑料'),
            (r'铜|铜材', '铜_纯铜'),
        ]

    def understand(self, user_input: str) -> Dict[str, Any]:
        """
        理解用户输入并返回结构化意图

        Args:
            user_input: 用户自然语言输入

        Returns:
            包含以下字段的字典:
            - action: IntentAction枚举
            - object: IntentObject枚举 (可选)
            - dimensions: 尺寸列表 [x, y, z] (可选)
            - material: 材料字符串 (可选)
            - confidence: 置信度 (0-1)
            - error: 错误信息 (可选)
            - fallback: 是否降级到本地模式 (可选)
        """
        # 输入验证
        if not user_input or not user_input.strip():
            return {
                "action": None,
                "object": None,
                "dimensions": None,
                "material": None,
                "confidence": 0,
                "error": "Empty input"
            }

        # 选择理解模式
        if self.use_claude and self.claude_client:
            try:
                return self._understand_with_claude(user_input)
            except Exception as e:
                print(f"Claude API failed: {e}, falling back to local mode")
                return self._understand_local(user_input, fallback=True)
        else:
            return self._understand_local(user_input, fallback=False)

    def _understand_with_claude(self, user_input: str) -> Dict[str, Any]:
        """
        使用Claude API进行意图理解

        Args:
            user_input: 用户输入

        Returns:
            结构化意图字典
        """
        # 构造提示词
        prompt = f"""你是SolidWorks 2026的意图理解助手。请分析用户输入并返回结构化的意图。

用户输入: "{user_input}"

请返回JSON格式的意图,包含以下字段:
- action: 动作 (create/modify/delete/analyze/export/import/assembly/drawing)
- object: 对象 (part/assembly/drawing/feature/sketch)
- dimensions: 尺寸 [x,y,z] (如果提到)
- material: 材料 (如果提到)
- confidence: 置信度 0-1

只返回JSON,不要其他内容。"""

        try:
            # 调用Claude API
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 解析响应
            response_text = message.content[0].text
            result = json.loads(response_text)

            # 转换为枚举类型
            if "action" in result and result["action"]:
                result["action"] = IntentAction(result["action"])
            if "object" in result and result["object"]:
                result["object"] = IntentObject(result["object"])

            return result

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Claude response: {e}")
        except Exception as e:
            raise Exception(f"Claude API call failed: {e}")

    def _understand_local(self, user_input: str, fallback: bool = False) -> Dict[str, Any]:
        """
        使用本地规则进行意图理解

        Args:
            user_input: 用户输入
            fallback: 是否为降级模式

        Returns:
            结构化意图字典
        """
        result = {
            "action": None,
            "object": None,
            "dimensions": None,
            "material": None,
            "confidence": 0.0,
        }

        if fallback:
            result["fallback"] = True

        # 1. 识别动作
        action, action_confidence = self._match_action(user_input)
        result["action"] = action
        result["confidence"] += action_confidence * 0.5

        # 2. 识别对象
        obj, object_confidence = self._match_object(user_input)
        result["object"] = obj
        result["confidence"] += object_confidence * 0.3

        # 3. 提取尺寸
        dimensions = self._extract_dimensions(user_input)
        if dimensions:
            result["dimensions"] = dimensions
            result["confidence"] += 0.1

        # 4. 提取材料
        material = self._extract_material(user_input)
        if material:
            result["material"] = material
            result["confidence"] += 0.1

        # 确保置信度在0-1范围内
        result["confidence"] = min(1.0, result["confidence"])

        return result

    def _match_action(self, text: str) -> tuple[Optional[IntentAction], float]:
        """
        匹配动作

        Returns:
            (动作, 置信度)
        """
        text_lower = text.lower()

        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # 计算置信度: 精确匹配 > 模糊匹配
                    confidence = 0.9 if re.search(rf'^{pattern}', text, re.IGNORECASE) else 0.7
                    return action, confidence

        # 默认返回CREATE (对于模糊输入)
        return IntentAction.CREATE, 0.3

    def _match_object(self, text: str) -> tuple[Optional[IntentObject], float]:
        """
        匹配对象

        Returns:
            (对象, 置信度)
        """
        text_lower = text.lower()

        for obj, patterns in self.object_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    confidence = 0.8
                    return obj, confidence

        return None, 0.0

    def _extract_dimensions(self, text: str) -> Optional[List[float]]:
        """
        提取尺寸参数

        Returns:
            尺寸列表 [x, y, z] 或 None
        """
        for pattern in self.dimension_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    dimensions = [float(match.group(i)) for i in range(1, 4)]
                    return dimensions
                except (ValueError, IndexError):
                    continue

        return None

    def _extract_material(self, text: str) -> Optional[str]:
        """
        提取材料信息

        Returns:
            材料字符串或None
        """
        for pattern, material in self.material_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return material

        return None


# ==================== 辅助函数 ====================

def demo_understanding():
    """演示意图理解功能"""
    print("=" * 60)
    print("意图理解模块演示")
    print("=" * 60)

    # 本地模式演示
    print("\n【本地模式演示】")
    intent = IntentUnderstanding(use_claude=False)

    test_inputs = [
        "创建一个方块",
        "修改零件尺寸",
        "分析质量属性",
        "导出STEP格式",
        "100x100x50mm的方块",
        "铝合金方块",
        "做东西",
        "创建带M10安装孔的轴承座",
    ]

    for user_input in test_inputs:
        result = intent.understand(user_input)
        print(f"\n输入: {user_input}")
        result_json = json.dumps({
            'action': result['action'].value if result['action'] else None,
            'object': result['object'].value if result['object'] else None,
            'dimensions': result['dimensions'],
            'material': result['material'],
            'confidence': result['confidence']
        }, ensure_ascii=False, indent=2)
        print(f"结果: {result_json}")

    # Claude模式演示 (如果可用)
    print("\n【Claude API模式演示】")
    try:
        intent_claude = IntentUnderstanding(use_claude=True)
        if intent_claude.use_claude:
            result = intent_claude.understand("创建方块")
            print(f"\n输入: 创建方块")
            print(f"结果: {json.dumps(result, default=str, ensure_ascii=False, indent=2)}")
        else:
            print("Claude API不可用，已降级到本地模式")
    except Exception as e:
        print(f"Claude模式初始化失败: {e}")


if __name__ == "__main__":
    demo_understanding()
