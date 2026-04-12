#!/usr/bin/env python3
"""
示例：自动生成工程图
从 3D 零件自动生成带标准三视图的工程图

使用方式：
    python auto_drawing.py [--input PART_PATH] [--output OUTPUT_PATH]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sw_connection import SWConnection
from sw_drawing import SWDrawing
from sw_export import SWExport


def main():
    parser = argparse.ArgumentParser(description="SolidWorks 自动出图工具")
    parser.add_argument("--input", required=True, help="零件/装配体文件路径")
    parser.add_argument("--output", default=None, help="输出路径（默认与输入同目录）")
    parser.add_argument("--format", default="slddrw", help="输出格式 (slddrw/pdf/dxf)")
    args = parser.parse_args()

    if args.output is None:
        base = os.path.splitext(args.input)[0]
        ext_map = {"slddrw": ".slddrw", "pdf": ".pdf", "dxf": ".dxf"}
        args.output = base + ext_map.get(args.format, ".slddrw")

    conn = SWConnection()
    conn.connect(startup=True)

    try:
        drawing = SWDrawing(conn)

        # 从零件创建工程图
        print(f"从零件创建工程图: {args.input}")
        drawing.create_drawing_from_part(args.input)

        # 添加标准三视图
        print("添加标准三视图...")
        views = drawing.add_standard_views(args.input)

        # 添加等轴测视图
        print("添加等轴测视图...")
        drawing.add_isometric_view(args.input)

        # 填写标题栏
        drawing.add_title_block_info(
            part_number=os.path.splitext(os.path.basename(args.input))[0],
            description="自动生成的工程图",
            drawn_by="Claude AI",
            scale="1:1",
        )

        # 尝试自动标注尺寸（SW2026 AI 功能）
        try:
            print("执行自动尺寸标注...")
            drawing.auto_dimension()
        except Exception as e:
            print(f"自动标注需要 SolidWorks 2026 AI 支持: {e}")

        # 保存工程图
        from sw_operations import SWOperations
        ops = SWOperations(conn)
        ops.save_file(args.output)
        print(f"工程图已保存: {args.output}")

        # 如果需要导出为 PDF
        if args.format == "pdf":
            pdf_path = os.path.splitext(args.output)[0] + ".pdf"
            exporter = SWExport(conn)
            exporter.export_pdf(pdf_path)
            print(f"PDF 已导出: {pdf_path}")

    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
