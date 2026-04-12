"""
测试结果验证器模块

对应需求文档: 文档/需求/req_result_validator.md
测试原则: 使用 mock 隔离外部依赖
"""

import pytest
from typing import Dict, List
from dataclasses import dataclass
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from 代码.Python脚本.result_validator import ResultValidator, ValidationReport


class TestResultValidator:
    """测试结果验证器"""

    @pytest.mark.parametrize("test_id,results,intent,expected", [
        (
            "V-01",
            [{"feature": "Extrude", "status": "success"}],
            {"type": "box", "size": [100, 100, 50]},
            {"success": True, "passed": 1, "failed": 0, "warnings": 1}  # 有metrics警告
        ),
        (
            "V-02",
            [{"feature": "Extrude", "status": "failed", "error": "Sketch invalid"}],
            {"type": "box"},
            {"success": False, "passed": 0, "failed": 1, "warnings": 1}  # 有 metrics 警告
        ),
        (
            "V-12",
            [{"thickness": 5, "draft": 3, "fillet": 2, "metrics": {"mass": 1000, "volume": 400000}}],
            {"thickness": 5},
            {"success": True, "passed": 3, "failed": 0, "warnings": 0, "metrics": {"mass": 1000, "volume": 400000}}  # 3个设计规则，有metrics
        ),
    ])
    def test_validate_task_execution(self, test_id, results, intent, expected):
        """测试任务执行验证 - V-01, V-02, V-12"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator()
        report = validator.validate(results, intent)

        assert report.success == expected["success"]
        assert report.passed == expected["passed"]
        assert report.failed == expected["failed"]
        assert len(report.warnings) == expected["warnings"]

        if "metrics" in expected:
            assert report.metrics == expected["metrics"]

    @pytest.mark.parametrize("test_id,results,intent,knowledge_base,expected_warning", [
        (
            "V-03",
            [{"feature": "Shell", "thickness": 2}],
            {"min_thickness": 3},
            {"min_thickness": 3},
            "壁厚 2mm 小于最小值 3mm"
        ),
        (
            "V-04",
            [{"feature": "Draft", "angle": 0.5}],
            {"draft_angle": 1},
            {"min_draft": 1},
            "拔模角度 0.5° 小于最小值 1°"
        ),
        (
            "V-05",
            [{"feature": "Fillet", "radius": 0.5}],
            {},
            {"min_fillet": 1},
            "圆角半径 0.5mm 小于最小值 1mm"
        ),
    ])
    def test_design_rules_checking(self, test_id, results, intent, knowledge_base, expected_warning):
        """测试设计规则检查 - V-03, V-04, V-05"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator(knowledge_base)
        report = validator.validate(results, intent)

        # 警告不影响成功状态，但应该有警告信息
        assert expected_warning in report.warnings

    @pytest.mark.parametrize("test_id,results,intent,expected", [
        (
            "V-06",
            [{"metrics": {"mass": 1500, "volume": 500000}}],
            {},
            {"success": True, "metrics": {"mass": 1500, "volume": 500000}}
        ),
        (
            "V-10",
            [{"feature": "Extrude", "status": "success"}],
            {},
            {
                "success": True,
                "metrics": {"mass": 0, "volume": 0},
                "warning_contains": "无法获取质量指标"
            }
        ),
    ])
    def test_metric_calculation(self, test_id, results, intent, expected):
        """测试指标计算 - V-06, V-10"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator()
        report = validator.validate(results, intent)

        assert report.success == expected["success"]
        assert report.metrics == expected["metrics"]

        if "warning_contains" in expected:
            assert any(expected["warning_contains"] in w for w in report.warnings)

    @pytest.mark.parametrize("test_id,results,intent,knowledge_base,expected_suggestion", [
        (
            "V-07",
            [{"feature": "Extrude", "depth": 5}],
            {"min_depth": 10},
            {},
            "建议增加拉伸深度至至少 10mm"
        ),
    ])
    def test_suggestion_generation(self, test_id, results, intent, knowledge_base, expected_suggestion):
        """测试建议生成 - V-07"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator(knowledge_base)
        report = validator.validate(results, intent)

        # 建议生成不影响成功状态
        assert expected_suggestion in report.suggestions

    @pytest.mark.parametrize("test_id,results,intent,expected_error", [
        (
            "V-08",
            [{"feature": "Extrude", "depth": 50}],
            {"depth": 100},
            "Extrude depth 50mm 不符合设计意图 100mm"
        ),
    ])
    def test_intent_validation(self, test_id, results, intent, expected_error):
        """测试意图验证 - V-08"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator()
        report = validator.validate(results, intent)

        assert report.success is False
        assert expected_error in report.errors

    @pytest.mark.parametrize("test_id,results,intent,expected_error", [
        (
            "V-09",
            [],
            {"type": "box"},
            "没有可验证的结果"
        ),
    ])
    def test_empty_results(self, test_id, results, intent, expected_error):
        """测试空结果处理 - V-09"""
        from 代码.Python脚本.result_validator import ResultValidator

        validator = ResultValidator()
        report = validator.validate(results, intent)

        assert report.success is False
        assert expected_error in report.errors

    def test_multiple_design_rules(self):
        """测试多项设计规则同时检查 - V-11"""
        from 代码.Python脚本.result_validator import ResultValidator

        results = [{"thickness": 2, "draft": 0.5, "fillet": 0.5}]
        intent = {}
        knowledge_base = {"min_thickness": 3, "min_draft": 1, "min_fillet": 1}

        validator = ResultValidator(knowledge_base)
        report = validator.validate(results, intent)

        # 警告不影响成功状态
        assert "壁厚 2mm 小于最小值 3mm" in report.warnings
        assert "拔模角度 0.5° 小于最小值 1°" in report.warnings
        assert "圆角半径 0.5mm 小于最小值 1mm" in report.warnings
        # 由于没有 metrics，会有额外的警告
        assert len(report.warnings) >= 3

    def test_validator_initialization(self):
        """测试验证器初始化"""
        from 代码.Python脚本.result_validator import ResultValidator

        # 测试默认知识库（空字典会触发默认规则）
        validator1 = ResultValidator()
        # 空字典会被填充为默认规则
        assert "min_thickness" in validator1.knowledge_base
        assert "min_draft" in validator1.knowledge_base
        assert "min_fillet" in validator1.knowledge_base

        # 测试自定义知识库
        kb = {"min_thickness": 5, "min_draft": 2}
        validator2 = ResultValidator(kb)
        assert validator2.knowledge_base == kb

    def test_validation_report_structure(self):
        """测试验证报告结构"""
        from 代码.Python脚本.result_validator import ValidationReport

        report = ValidationReport(success=True)

        assert report.success is True
        assert report.passed == 0
        assert report.failed == 0
        assert report.warnings == []
        assert report.errors == []
        assert report.suggestions == []
        assert report.metrics == {}
