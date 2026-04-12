#!/usr/bin/env python3
"""
示例：装配体信息提取与报告生成
读取装配体结构、零件列表、质量属性等信息

使用方式：
    python assembly_report.py [--input ASSEMBLY_PATH] [--output REPORT_PATH]
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sw_connection import SWConnection


def extract_bom(model, app) -> list:
    """提取 BOM（物料清单）"""
    bom = []

    # 获取装配体中的所有组件
    components = model.GetComponents(False)

    if components is None:
        return bom

    for comp in components:
        try:
            part_info = {
                "name": comp.Name2 if hasattr(comp, "Name2") else "Unknown",
                "path": comp.GetPathName() if hasattr(comp, "GetPathName") else "",
                "suppressed": comp.IsSuppressed() if hasattr(comp, "IsSuppressed") else False,
            }

            # 尝试获取质量属性
            try:
                mass_props = comp.GetMassProperties()
                if mass_props:
                    part_info["mass_kg"] = round(mass_props[0], 4)
                    part_info["volume_m3"] = round(mass_props[1], 6)
                    part_info["center_of_mass"] = [
                        round(v, 4) for v in mass_props[2:5]
                    ]
            except Exception:
                pass

            bom.append(part_info)

        except Exception as e:
            print(f"  警告: 无法读取组件信息: {e}")

    return bom


def extract_custom_properties(model) -> dict:
    """提取自定义属性"""
    properties = {}
    try:
        prop_manager = model.Extension.CustomPropertyManager("")
        names = prop_manager.GetAll("")

        if names:
            for name in names:
                value = prop_manager.Get(name)
                properties[name] = value[1] if isinstance(value, tuple) else value

    except Exception as e:
        print(f"  警告: 无法读取自定义属性: {e}")

    return properties


def generate_report(assembly_path: str, bom: list, properties: dict) -> dict:
    """生成结构化报告"""
    report = {
        "report_date": datetime.now().isoformat(),
        "assembly_file": assembly_path,
        "total_components": len(bom),
        "active_components": sum(1 for c in bom if not c.get("suppressed", False)),
        "suppressed_components": sum(1 for c in bom if c.get("suppressed", False)),
        "custom_properties": properties,
        "bill_of_materials": bom,
    }

    # 计算总质量
    total_mass = sum(c.get("mass_kg", 0) for c in bom if not c.get("suppressed", False))
    report["total_mass_kg"] = round(total_mass, 4)

    return report


def print_report(report: dict):
    """打印格式化报告"""
    print("\n" + "=" * 60)
    print("  装配体分析报告")
    print("=" * 60)
    print(f"  文件: {report['assembly_file']}")
    print(f"  日期: {report['report_date']}")
    print(f"  总组件数: {report['total_components']}")
    print(f"  活跃组件: {report['active_components']}")
    print(f"  压缩组件: {report['suppressed_components']}")
    print(f"  总质量: {report['total_mass_kg']} kg")
    print("-" * 60)

    print("\n  BOM 明细:")
    print(f"  {'序号':<6}{'名称':<30}{'质量(kg)':<12}{'状态':<8}")
    print(f"  {'-'*6}{'-'*30}{'-'*12}{'-'*8}")

    for i, comp in enumerate(report["bill_of_materials"], 1):
        status = "压缩" if comp.get("suppressed") else "活跃"
        mass = f"{comp.get('mass_kg', 'N/A')}"
        print(f"  {i:<6}{comp['name']:<30}{mass:<12}{status:<8}")

    if report["custom_properties"]:
        print("\n  自定义属性:")
        for key, value in report["custom_properties"].items():
            print(f"    {key}: {value}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="SolidWorks 装配体报告工具")
    parser.add_argument("--input", required=True, help="装配体文件路径 (.sldasm)")
    parser.add_argument("--output", default=None, help="报告输出路径 (.json)")
    args = parser.parse_args()

    if args.output is None:
        args.output = os.path.splitext(args.input)[0] + "_report.json"

    conn = SWConnection()
    conn.connect()

    try:
        print(f"打开装配体: {args.input}")
        model = conn.open_file(args.input)

        # 验证是装配体
        doc_type = conn.get_model_type(model)
        if doc_type != "assembly":
            print(f"错误: 文件类型为 {doc_type}，需要装配体 (.sldasm)")
            return

        # 提取信息
        print("提取 BOM...")
        bom = extract_bom(model, conn.app)

        print("提取自定义属性...")
        properties = extract_custom_properties(model)

        # 生成报告
        report = generate_report(args.input, bom, properties)

        # 打印报告
        print_report(report)

        # 保存 JSON 报告
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存: {args.output}")

    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
