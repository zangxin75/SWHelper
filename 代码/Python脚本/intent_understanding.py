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
from typing import Optional, Dict, Any, List

from schemas import Intent, ActionType, ObjectType


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
        # 动作关键词模式（使用ActionType）
        self.action_patterns = {
            ActionType.CREATE: [
                r'创建|生成|新建|增加|画|绘制|make|create|draw',
                r'做一个?|做一个?.+',
                r'做.+',  # 匹配"做"后跟任意字符（如"做东西"）
                r'帮我.+',  # 匹配"帮我"后跟任意字符（如"帮我处理"）
            ],
            ActionType.MODIFY: [
                r'修改|改变|调整|更新|编辑|设置|modify|change|edit|update|set',
                r'处理|process',  # 匹配"处理"动作
                r'添加|add',  # FIX-04: "添加"特征操作是MODIFY
                r'打|punch',  # FIX-04: "打"孔操作是MODIFY
            ],
            ActionType.ANALYZE: [
                r'分析|计算|测量|检查|评估|analyze|calculate|measure|check',
            ],
            ActionType.EXPORT: [
                r'导出|保存|输出|export|save|output',
            ],
        }

        # 对象关键词模式（使用ObjectType）
        self.object_patterns = {
            ObjectType.PART: [
                r'零件|部件|实体|方块|圆柱|球体|part|component|solid|body',
                r'方块|圆柱|球体|立方体|长方体',
            ],
            ObjectType.ASSEMBLY: [
                r'装配体|装配|组件|产品|assembly',
            ],
            ObjectType.DRAWING: [
                r'工程图|视图|图纸|drawing|view|draft',
            ],
            ObjectType.FEATURE: [
                r'特征|拉伸|旋转|扫描|放样|feature|extrude|revolve|sweep|loft',
                r'孔|倒角|圆角|fillet|chamfer|hole',
                r'凸台|切除|筋|boss|cut|rib',  # FIX-04: 添加常见特征
            ],
            ObjectType.SKETCH: [
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
            # FIX-06: 匹配中英文混合尺寸
            r'(\d+(?:\.\d+)?)\s*mm?\s*[xX]\s*(\d+(?:\.\d+)?)\s*mm?\s*[xX]\s*(\d+(?:\.\d+)?)\s*mm?',
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

    def understand(self, user_input: str) -> Intent:
        """
        理解用户输入并返回结构化意图

        Args:
            user_input: 用户自然语言输入

        Returns:
            Intent对象，包含action, object_type, parameters, confidence等字段
        """
        # 步骤1：输入验证（FIX-01: 拒绝非结构化输入）
        validation_result = self._validate_input(user_input)
        if not validation_result["is_valid"]:
            # 返回低置信度的Intent，并在constraints中保存验证原因
            validation_reason = validation_result.get("reason", "无法理解")
            # 将None转换为空字符串以避免Pydantic验证错误
            safe_input = user_input if user_input is not None else ""
            return Intent(
                action=ActionType.UNKNOWN,
                object=ObjectType.UNKNOWN,
                parameters={},
                constraints=[validation_reason],  # 存储验证原因
                confidence=validation_result.get("confidence", 0.1),
                raw_input=safe_input
            )

        # 步骤2：选择理解模式
        if self.use_claude and self.claude_client:
            try:
                intent_dict = self._understand_with_claude(user_input)
            except Exception as e:
                print(f"Claude API failed: {e}, falling back to local mode")
                intent_dict = self._understand_local(user_input, fallback=True)
        else:
            intent_dict = self._understand_local(user_input, fallback=False)

        # 步骤3：将dict转换为Intent对象
        return self._dict_to_intent(intent_dict, user_input)

    def _validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        验证输入是否有效（FIX-01需求）

        Args:
            user_input: 用户输入

        Returns:
            验证结果字典，包含:
            - is_valid: bool
            - reason: str (如果无效)
            - confidence: float
        """
        # None检查
        if user_input is None:
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.0
            }

        # 空字符串检查
        if not user_input or not user_input.strip():
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.0
            }

        # 纯特殊字符检查（没有字母或汉字）
        if not re.search(r'[a-zA-Z\u4e00-\u9fff]', user_input):
            # 如果没有字母或汉字，视为无效
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.0
            }

        # 纯标点符号检查（使用string.punctuation）
        import string
        cleaned_input = user_input.strip()
        # 移除所有空格和标点符号
        for char in string.whitespace + string.punctuation:
            cleaned_input = cleaned_input.replace(char, '')
        if len(cleaned_input) == 0:
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.0
            }

        # 极短输入检查（单字）
        if len(user_input.strip()) <= 1:
            return {
                "is_valid": False,
                "reason": "信息不足",
                "confidence": 0.2
            }

        # FIX-06: 检查是否有尺寸格式（数字x数字x数字 + 单位）
        # 如果有尺寸格式，即使没有关键词也认为是有效的设计意图
        dimension_pattern = r'\d+(?:\.\d+)?\s*(?:mm|厘米|米|m|cm)\s*[xX]\s*\d+(?:\.\d+)?\s*(?:mm|厘米|米|m|cm)\s*[xX]\s*\d+(?:\.\d+)?\s*(?:mm|厘米|米|m|cm)'
        has_dimensions = re.search(dimension_pattern, user_input, re.IGNORECASE)

        # 无关键词检查（如果没有创建、修改等动词）
        # 包含常见动作词和模糊表达词（做、弄、帮我、处理等）
        # FIX-06: 添加对象词（方块、圆柱、装配体等）表示隐含的创建意图
        # FIX-06: 添加单位词（毫米、厘米、米、mm、cm、m）表示隐含的设计意图
        # ENH-02: 添加工程图关键词（图纸、视图、比例、使用、A0-A4等）
        keyword_pattern = r'创建|新建|生成|设计|修改|更改|调整|分析|计算|检查|导出|保存|输出|添加|删除|移除|做|弄|帮我|处理|打|方块|圆柱|球体|零件|装配|立方体|长方体|毫米|厘米|米|mm|cm|m|make|create|modify|change|analyze|export|add|delete|remove|do|help|process|cube|cylinder|sphere|part|assembly|使用|图纸|视图|比例|工程图|A0|A1|A2|A3|A4|drawing|view|sheet|scale|放大|缩小'
        if not has_dimensions and not re.search(keyword_pattern, user_input, re.IGNORECASE):
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.3
            }
            return {
                "is_valid": False,
                "reason": "无法理解",
                "confidence": 0.3
            }

        # 输入有效
        return {
            "is_valid": True,
            "confidence": 1.0
        }

    def _dict_to_intent(self, intent_dict: Dict[str, Any], raw_input: str) -> Intent:
        """
        将dict转换为Intent对象

        Args:
            intent_dict: 意图字典
            raw_input: 原始用户输入

        Returns:
            Intent对象
        """
        # 映射action字符串到ActionType枚举
        action_str = intent_dict.get("action")
        if action_str is None:
            action = ActionType.UNKNOWN
        else:
            action_mapping = {
                "create": ActionType.CREATE,
                "modify": ActionType.MODIFY,
                "analyze": ActionType.ANALYZE,
                "export": ActionType.EXPORT,
                "unknown": ActionType.UNKNOWN
            }
            action = action_mapping.get(action_str.lower(), ActionType.UNKNOWN)

        # 映射object字符串到ObjectType枚举
        object_str = intent_dict.get("object")
        if object_str is None:
            object_type = ObjectType.UNKNOWN
        else:
            object_mapping = {
                "part": ObjectType.PART,
                "assembly": ObjectType.ASSEMBLY,
                "drawing": ObjectType.DRAWING,
                "feature": ObjectType.FEATURE,
                "sketch": ObjectType.SKETCH,
                "unknown": ObjectType.UNKNOWN
            }
            object_type = object_mapping.get(object_str.lower(), ObjectType.UNKNOWN)

        # 构建parameters
        parameters = {}

        # 复制尺寸参数
        if "dimensions" in intent_dict and intent_dict["dimensions"]:
            parameters["dimensions"] = intent_dict["dimensions"]

        # 复制材料参数
        if "material" in intent_dict and intent_dict["material"]:
            parameters["material"] = intent_dict["material"]

        # ENH-01: 复制装配体参数
        assembly_param_keys = ["component_count", "mate_type", "check_type", "view_type", "is_subassembly"]
        for key in assembly_param_keys:
            if key in intent_dict and intent_dict[key] is not None:
                parameters[key] = intent_dict[key]

        # ENH-02: 复制工程图参数
        drawing_param_keys = ["view_count", "sheet_format", "scale", "annotation", "format"]
        for key in drawing_param_keys:
            if key in intent_dict and intent_dict[key] is not None:
                parameters[key] = intent_dict[key]

        # FIX-02: 添加特征信息到parameters
        if "feature_info" in intent_dict and intent_dict["feature_info"]:
            feature_info = intent_dict["feature_info"]
            # 将feature_info中的所有键值对添加到parameters
            for key, value in feature_info.items():
                parameters[key] = value

        # FIX-04: 如果对象是FEATURE，动作应该是MODIFY
        # 这处理"创建筋"、"创建凸台"等情况
        if object_type == ObjectType.FEATURE and action == ActionType.CREATE:
            action = ActionType.MODIFY

        return Intent(
            action=action,
            object=object_type,  # 注意：字段名是'object'不是'object_type'
            parameters=parameters,
            constraints=intent_dict.get("constraints", []),
            confidence=intent_dict.get("confidence", 0.5),
            raw_input=raw_input
        )

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
- action: 动作 (create/modify/analyze/export)
- object: 对象 (part/assembly/drawing/feature)
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

            # 不再转换为枚举，在_dict_to_intent中统一处理
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

        # 4.5. 提取装配体参数（ENH-01）
        # 检查是否识别为装配体对象（字符串或枚举）
        obj_is_assembly = (obj == "assembly" or
                           (hasattr(ObjectType, 'ASSEMBLY') and obj == ObjectType.ASSEMBLY) or
                           obj == ObjectType.ASSEMBLY)

        if obj_is_assembly:
            assembly_params = self._extract_assembly_params(user_input)
            if assembly_params:
                result.update(assembly_params)
                result["confidence"] += 0.05

        # 4.6. 提取工程图参数（ENH-02）
        # 检查是否识别为工程图对象（字符串或枚举）
        obj_is_drawing = (obj == "drawing" or
                          (hasattr(ObjectType, 'DRAWING') and obj == ObjectType.DRAWING) or
                          obj == ObjectType.DRAWING)

        if obj_is_drawing:
            drawing_params = self._extract_drawing_params(user_input)
            if drawing_params:
                result.update(drawing_params)
                result["confidence"] += 0.05

        # ENH-02: 隐式对象映射 - 如果检测到DRAWING特有操作，默认为DRAWING对象
        # 适用于"添加尺寸"、"添加注释"、"导出PDF"、"使用A3图纸"、"比例1:2"等
        if obj in [None, "unknown", "part", ObjectType.PART, "unknown", ObjectType.UNKNOWN]:
            # 检查是否是DRAWING特有的操作
            has_drawing_annotation = re.search(r'尺寸|标注|dimension|annotation', user_input, re.IGNORECASE)
            has_drawing_note = re.search(r'注释|注解|技术要求|note', user_input, re.IGNORECASE)
            has_drawing_export = re.search(r'导出.*[PDF|pdf]|PDF.*导出|export.*pdf|export_pdf', user_input, re.IGNORECASE)
            has_sheet_format = re.search(r'A[0-4]|图紙|图纸|sheet|使用', user_input, re.IGNORECASE)
            has_scale = re.search(r'比例|放大|缩小|scale|[0-9]+:[0-9]+', user_input, re.IGNORECASE)

            if has_drawing_annotation or has_drawing_note or has_drawing_export or has_sheet_format or has_scale:
                result["object"] = "drawing"
                result["confidence"] += 0.1

                # 如果之前没有检测到工程图参数，现在重新提取
                if "view_count" not in result and "sheet_format" not in result and "scale" not in result:
                    drawing_params = self._extract_drawing_params(user_input)
                    if drawing_params:
                        result.update(drawing_params)

        # 5. 提取特征信息（FIX-02）
        feature_info = self._extract_feature_info(user_input)
        if feature_info and ("feature_type" in feature_info or "features" in feature_info):
            result["feature_info"] = feature_info
            result["confidence"] += 0.05

            # FIX-02: 如果检测到特征操作，动作应该是MODIFY，对象应该是FEATURE
            # 无论当前action是什么，特征添加都是MODIFY操作
            result["action"] = "modify"
            result["object"] = "feature"

        # 确保置信度在0-1范围内
        result["confidence"] = min(1.0, result["confidence"])

        return result

    def _match_action(self, text: str) -> tuple[Optional[str], float]:
        """
        匹配动作

        Returns:
            (动作字符串, 置信度)
        """
        max_confidence = 0.0
        matched_action = None

        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # 计算置信度
                    confidence = 0.8
                    # 如果关键词在文本开头，置信度更高
                    if re.search(r'^' + pattern, text, re.IGNORECASE):
                        confidence = 0.9

                    if confidence > max_confidence:
                        max_confidence = confidence
                        matched_action = action.value  # 返回枚举的字符串值

        return matched_action, max_confidence

    def _match_object(self, text: str) -> tuple[Optional[str], float]:
        """
        匹配对象

        Returns:
            (对象字符串, 置信度)
        """
        max_confidence = 0.0
        matched_object = "part"  # 默认为part

        for obj, patterns in self.object_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # ENH-01: 给更具体的关键词更高的置信度
                    # ASSEMBLY: "装配体" 比较具体，优先级应该比 "零件" 高
                    if obj == ObjectType.ASSEMBLY and re.search(r'装配体', text):
                        confidence = 0.9  # 明确提到"装配体"
                    elif obj == ObjectType.ASSEMBLY and re.search(r'装配', text):
                        confidence = 0.8  # 提到"装配"但可能是不完整表达
                    elif obj == ObjectType.PART and re.search(r'零件', text):
                        confidence = 0.75  # "零件"关键词
                    else:
                        confidence = 0.7  # 默认置信度

                    if confidence > max_confidence:
                        max_confidence = confidence
                        matched_object = obj.value  # 返回枚举的字符串值

        return matched_object, max_confidence

    def _extract_dimensions(self, text: str) -> Optional[List[float]]:
        """
        提取尺寸参数（支持单位换算）

        Returns:
            尺寸列表 [x, y, z]（单位：mm）或 None

        单位换算规则（FIX-06）:
        - mm, 毫米 → x1
        - cm, 厘米 → x10
        - m, 米 → x1000
        """
        # 首先尝试带单位的尺寸提取
        # 匹配模式：数字+单位 格式，支持三个维度
        # 例如: 100mm x 10cm x 0.1m
        unit_pattern = r'(\d+(?:\.\d+)?)\s*(mm|毫米|cm|厘米|m|米)\s*[xX]\s*(\d+(?:\.\d+)?)\s*(mm|毫米|cm|厘米|m|米)\s*[xX]\s*(\d+(?:\.\d+)?)\s*(mm|毫米|cm|厘米|m|米)'

        match = re.search(unit_pattern, text, re.IGNORECASE)
        if match:
            try:
                values = [float(match.group(i)) for i in (1, 3, 5)]
                units = [match.group(i) for i in (2, 4, 6)]

                # 单位换算为mm
                result = []
                for value, unit in zip(values, units):
                    unit_lower = unit.lower()
                    if unit_lower in ['mm', '毫米']:
                        result.append(value)
                    elif unit_lower in ['cm', '厘米']:
                        result.append(value * 10)
                    elif unit_lower in ['m', '米']:
                        result.append(value * 1000)
                    else:
                        result.append(value)  # 默认不换算
                return result
            except (ValueError, IndexError):
                pass

        # 如果单位模式失败，使用原有的简单数字模式
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

    def _extract_assembly_params(self, text: str) -> Dict[str, Any]:
        """
        提取装配体特定参数（ENH-01）

        支持的参数：
        - component_count: 组件数量
        - mate_type: 配合类型（coaxial, coincident, parallel, perpendicular, distance, angle）
        - check_type: 检查类型（interference, clearance）
        - view_type: 视图类型（exploded, section, detail）
        - is_subassembly: 是否子装配体

        Returns:
            装配体参数字典
        """
        import re
        params = {}

        # 提取组件数量："包含3个零件"、"5个组件"
        count_match = re.search(r'包含\s*(\d+)\s*[个件]', text)
        if count_match:
            params["component_count"] = int(count_match.group(1))

        # 提取配合类型
        mate_keywords = {
            r'同轴': 'coaxial',
            r'重合': 'coincident',
            r'平行': 'parallel',
            r'垂直': 'perpendicular',
            r'距离': 'distance',
            r'角度': 'angle',
        }
        for keyword, mate_type in mate_keywords.items():
            if keyword in text:
                params["mate_type"] = mate_type
                break

        # 提取检查类型
        if re.search(r'干涉', text):
            params["check_type"] = "interference"
        elif re.search(r'间隙| clearance', text):
            params["check_type"] = "clearance"

        # 提取视图类型
        if re.search(r'爆炸', text):
            params["view_type"] = "exploded"
        elif re.search(r'剖面| section', text):
            params["view_type"] = "section"
        elif re.search(r'详图| detail', text):
            params["view_type"] = "detail"

        # 提取子装配体
        if re.search(r'子装配|子组件| subassembly', text):
            params["is_subassembly"] = True

        return params

    def _extract_drawing_params(self, text: str) -> Dict[str, Any]:
        """
        提取工程图特定参数（ENH-02）

        支持的参数：
        - view_count: 视图数量（如"3个视图"）
        - sheet_format: 图纸格式（A0, A1, A2, A3, A4）
        - scale: 比例（如"1:2", "2:1"）
        - annotation: 标注类型（dimensions, note）

        Returns:
            工程图参数字典
        """
        import re
        params = {}

        # 提取视图数量："3个视图"、"包含前视俯视左视"
        view_count_match = re.search(r'(\d+)\s*[个份]\s*视图', text)
        if view_count_match:
            params["view_count"] = int(view_count_match.group(1))
        elif re.search(r'[前后左右顶底上下][视视][视图]', text):
            # 计算实际视图关键词数量
            view_keywords = re.findall(r'前视|后视|左视|右视|顶视|俯视|底视|上视', text)
            if view_keywords:
                params["view_count"] = len(set(view_keywords))  # 去重

        # 提取图纸格式
        sheet_keywords = {
            r'A0': 'A0',
            r'A1': 'A1',
            r'A2': 'A2',
            r'A3': 'A3',
            r'A4': 'A4',
        }
        for keyword, format_type in sheet_keywords.items():
            if re.search(keyword, text, re.IGNORECASE):
                params["sheet_format"] = format_type
                break

        # 提取比例："比例1:2"、"1:2比例"、"放大2倍"等
        scale_match = re.search(r'比例\s*([\d.]+)\s*:\s*([\d.]+)|([\d.]+)\s*:\s*([\d.]+)\s*比例', text)
        if scale_match:
            # 尝试两种模式
            if scale_match.group(1) and scale_match.group(2):
                params["scale"] = f"{scale_match.group(1)}:{scale_match.group(2)}"
            elif scale_match.group(3) and scale_match.group(4):
                params["scale"] = f"{scale_match.group(3)}:{scale_match.group(4)}"
        else:
            # 检查"放大X倍"
            zoom_match = re.search(r'放大\s*([\d.]+)\s*[倍倍]', text)
            if zoom_match:
                params["scale"] = f"{zoom_match.group(1)}:1"
            # 检查"缩小X倍"
            shrink_match = re.search(r'缩小\s*([\d.]+)\s*[倍倍]', text)
            if shrink_match:
                params["scale"] = f"1:{shrink_match.group(1)}"

        # 提取标注类型
        if re.search(r'尺寸|标注|dimension', text, re.IGNORECASE):
            params["annotation"] = "dimensions"
        elif re.search(r'注释|注解|技术要求|note', text, re.IGNORECASE):
            params["annotation"] = "note"

        # 提取导出格式：PDF、STEP、DXF等
        export_format_match = re.search(r'(PDF|pdf|STEP|step|DXF|dxf)', text)
        if export_format_match:
            params["format"] = export_format_match.group(1).lower()

        return params

    def _extract_feature_info(self, text: str) -> Dict[str, Any]:
        """
        提取特征信息（FIX-02）

        支持的特征类型：
        - 倒角：提取distance参数
        - 圆角：提取radius参数
        - 孔：提取diameter参数
        - 阵列：提取spacing、count参数

        支持多特征：用"和"连接的特征会被识别为多个

        Returns:
            特征信息字典，包含feature_type和对应参数，或features列表（多特征时）
        """
        import re

        # 检查是否有多个特征（用"和"连接）
        if '和' in text:
            # 分割为多个特征描述
            parts = text.split('和')
            features = []
            for part in parts:
                feature = self._extract_single_feature(part.strip())
                if feature:
                    features.append(feature)
            if features:
                return {"features": features}

        # 单特征情况
        return self._extract_single_feature(text)

    def _extract_single_feature(self, text: str) -> Dict[str, Any]:
        """提取单个特征的信息"""
        import re

        feature_info = {}

        # 检测特征类型
        if re.search(r'倒角|chamfer', text, re.IGNORECASE):
            feature_info["feature_type"] = "chamfer"
            # 提取尺寸（如"10mm倒角"、"倒角10mm"）
            size_match = re.search(r'(\d+(?:\.\d+)?)\s*mm?\s*倒角|倒角\s*(\d+(?:\.\d+)?)\s*mm?', text, re.IGNORECASE)
            if size_match:
                size = float(size_match.group(1) if size_match.group(1) else size_match.group(2))
                feature_info["distance"] = size

        elif re.search(r'圆角|fillet', text, re.IGNORECASE):
            feature_info["feature_type"] = "fillet"
            # 提取半径（如"5mm圆角"、"圆角5mm"）
            radius_match = re.search(r'(\d+(?:\.\d+)?)\s*mm?\s*圆角|圆角\s*(\d+(?:\.\d+)?)\s*mm?', text, re.IGNORECASE)
            if radius_match:
                radius = float(radius_match.group(1) if radius_match.group(1) else radius_match.group(2))
                feature_info["radius"] = radius

        elif re.search(r'孔|hole', text, re.IGNORECASE):
            feature_info["feature_type"] = "hole"
            # 提取直径（如"直径10mm的孔"、"孔直径10mm"）
            diameter_match = re.search(r'直径\s*(\d+(?:\.\d+)?)\s*mm?\s*的孔|孔.*?直径\s*(\d+(?:\.\d+)?)\s*mm?', text, re.IGNORECASE)
            if diameter_match:
                diameter = float(diameter_match.group(1) if diameter_match.group(1) else diameter_match.group(2))
                feature_info["diameter"] = diameter

        elif re.search(r'阵列|pattern', text, re.IGNORECASE):
            feature_info["feature_type"] = "pattern"
            # 提取间距
            spacing_match = re.search(r'间距\s*(\d+(?:\.\d+)?)\s*mm?', text, re.IGNORECASE)
            if spacing_match:
                feature_info["spacing"] = float(spacing_match.group(1))
            # 提取数量
            count_match = re.search(r'数量\s*(\d+)', text, re.IGNORECASE)
            if count_match:
                feature_info["count"] = int(count_match.group(1))

        return feature_info


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
