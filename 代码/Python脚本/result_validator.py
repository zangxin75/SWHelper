"""
结果验证器模块

功能:
1. 验证任务执行状态
2. 检查设计规则符合性
3. 计算设计指标（质量、体积）
4. 生成验证报告和改进建议
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationReport:
    """验证报告"""
    success: bool              # 整体验证是否通过
    passed: int = 0            # 通过的验证项数量
    failed: int = 0            # 失败的验证项数量
    warnings: List[str] = None # 警告列表（不符合设计规则）
    errors: List[str] = None   # 错误列表（任务失败、参数不匹配）
    suggestions: List[str] = None  # 改进建议
    metrics: Dict[str, float] = None  # 设计指标（质量、体积等）

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.suggestions is None:
            self.suggestions = []
        if self.metrics is None:
            self.metrics = {}


class ResultValidator:
    """结果验证器"""

    def __init__(self, knowledge_base: Optional[Dict] = None):
        """
        初始化验证器

        Args:
            knowledge_base: 设计知识库，包含设计规则（如最小壁厚、最小拔模角度等）
        """
        self.knowledge_base = knowledge_base or {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认设计规则（仅当知识库为空时）"""
        if not self.knowledge_base:
            default_rules = {
                "min_thickness": 3,      # 最小壁厚 (mm)
                "min_draft": 1,          # 最小拔模角度 (degree)
                "min_fillet": 1,         # 最小圆角半径 (mm)
            }
            self.knowledge_base = default_rules

    def validate(self, results: List[Dict], intent: Dict) -> ValidationReport:
        """
        验证设计结果

        Args:
            results: 任务执行结果列表
            intent: 原始设计意图

        Returns:
            ValidationReport: 验证报告
        """
        report = ValidationReport(success=True)

        # V-09: 检查空结果
        if not results:
            report.success = False
            report.errors.append("没有可验证的结果")
            return report

        # 验证任务执行状态
        self._validate_task_execution(results, report)

        # 验证设计意图符合性
        self._validate_intent_compliance(results, intent, report)

        # 检查设计规则
        self._check_design_rules(results, report)

        # 计算指标
        self._calculate_metrics(results, report)

        # 生成改进建议
        self._generate_suggestions(results, intent, report)

        # 判断整体成功状态
        # 有错误、失败任务或设计规则警告都视为失败
        if report.failed > 0 or report.errors:
            report.success = False

        return report

    def _validate_task_execution(self, results: List[Dict], report: ValidationReport):
        """验证任务执行状态"""
        for result in results:
            status = result.get("status", "")

            if status == "success":
                report.passed += 1
            elif status == "failed":
                report.failed += 1
                error_msg = result.get("error", "未知错误")
                report.errors.append(f"任务失败: {error_msg}")

    def _validate_intent_compliance(self, results: List[Dict], intent: Dict, report: ValidationReport):
        """验证结果是否符合设计意图"""
        for result in results:
            for key, intent_value in intent.items():
                if key in result:
                    actual_value = result[key]

                    # 数值类型比较
                    if isinstance(intent_value, (int, float)) and isinstance(actual_value, (int, float)):
                        if abs(actual_value - intent_value) > 0.01:  # 允许小误差
                            report.failed += 1
                            feature_name = result.get("feature", "未知特征")
                            # 修正错误消息格式，添加空格
                            param_name = key if not key.startswith("min_") else key.replace("min_", "")
                            report.errors.append(
                                f"{feature_name} {param_name} {actual_value}mm 不符合设计意图 {intent_value}mm"
                            )

    def _check_design_rules(self, results: List[Dict], report: ValidationReport):
        """检查设计规则符合性"""
        for result in results:
            # 通过的规则检查计数（初始化为0，每个结果最多计数一次）
            rule_checks_passed = 0
            total_rule_checks = 0

            # 检查壁厚
            if "thickness" in result:
                total_rule_checks += 1
                thickness = result["thickness"]
                min_thickness = self.knowledge_base.get("min_thickness", 3)
                if thickness < min_thickness:
                    report.warnings.append(f"壁厚 {thickness}mm 小于最小值 {min_thickness}mm")
                else:
                    rule_checks_passed += 1

            # 检查拔模角度
            if "draft" in result or "angle" in result:
                total_rule_checks += 1
                angle = result.get("draft", result.get("angle", 0))
                min_draft = self.knowledge_base.get("min_draft", 1)
                if angle < min_draft:
                    report.warnings.append(f"拔模角度 {angle}° 小于最小值 {min_draft}°")
                else:
                    rule_checks_passed += 1

            # 检查圆角半径
            if "fillet" in result or "radius" in result:
                total_rule_checks += 1
                radius = result.get("fillet", result.get("radius", 0))
                min_fillet = self.knowledge_base.get("min_fillet", 1)
                if radius < min_fillet:
                    report.warnings.append(f"圆角半径 {radius}mm 小于最小值 {min_fillet}mm")
                else:
                    rule_checks_passed += 1

            # 如果所有规则检查都通过，增加 passed 计数
            if total_rule_checks > 0 and rule_checks_passed == total_rule_checks:
                report.passed += rule_checks_passed

    def _calculate_metrics(self, results: List[Dict], report: ValidationReport):
        """计算设计指标"""
        has_metrics = False

        for result in results:
            if "metrics" in result:
                metrics = result["metrics"]
                if isinstance(metrics, dict):
                    report.metrics.update(metrics)
                    has_metrics = True

        # V-10: 如果没有指标数据，使用默认值
        if not has_metrics:
            report.metrics = {"mass": 0, "volume": 0}
            report.warnings.append("无法获取质量指标")

    def _generate_suggestions(self, results: List[Dict], intent: Dict, report: ValidationReport):
        """生成改进建议"""
        for result in results:
            # 基于意图生成建议
            for key, intent_value in intent.items():
                if key in result and key.startswith("min_"):
                    actual_value = result[key]
                    if actual_value < intent_value:
                        feature_name = result.get("feature", "特征")
                        param_name = key.replace("min_", "").replace("_", " ")
                        report.suggestions.append(
                            f"建议增加{feature_name}{param_name}至至少 {intent_value}mm"
                        )

            # 基于设计规则生成建议
            if "thickness" in result:
                thickness = result["thickness"]
                min_thickness = self.knowledge_base.get("min_thickness", 3)
                if thickness < min_thickness:
                    report.suggestions.append(f"建议增加壁厚至至少 {min_thickness}mm")

            if "draft" in result or "angle" in result:
                angle = result.get("draft", result.get("angle", 0))
                min_draft = self.knowledge_base.get("min_draft", 1)
                if angle < min_draft:
                    report.suggestions.append(f"建议增加拔模角度至至少 {min_draft}°")

            if "fillet" in result or "radius" in result:
                radius = result.get("fillet", result.get("radius", 0))
                min_fillet = self.knowledge_base.get("min_fillet", 1)
                if radius < min_fillet:
                    report.suggestions.append(f"建议增加圆角半径至至少 {min_fillet}mm")

            # V-07: 特定场景建议生成
            if result.get("feature") == "Extrude" and "depth" in result:
                depth = result["depth"]
                min_depth = intent.get("min_depth", 0)
                if min_depth > 0 and depth < min_depth:
                    report.suggestions.append(f"建议增加拉伸深度至至少 {min_depth}mm")
