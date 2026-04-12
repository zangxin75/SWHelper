#!/usr/bin/env python3
"""
示例：批量导出文件
将指定目录下的 SolidWorks 零件批量导出为 STEP 和 STL 格式

使用方式：
    python batch_export.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--formats step,stl]
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sw_connection import SWConnection
from sw_export import SWExport
from batch_runner import BatchRunner


def main():
    parser = argparse.ArgumentParser(description="SolidWorks 批量导出工具")
    parser.add_argument("--input", default=r"D:\sw2026_parts", help="输入目录")
    parser.add_argument("--output", default=r"D:\sw2026_output", help="输出目录")
    parser.add_argument(
        "--formats", default="step,stl",
        help="导出格式，逗号分隔 (step,stl,iges,pdf,dxf,dwg)"
    )
    args = parser.parse_args()

    formats = [f.strip() for f in args.formats.split(",")]

    conn = SWConnection()
    conn.connect(startup=True)

    try:
        runner = BatchRunner(conn)
        exporter = SWExport(conn)

        # 扫描输入目录
        print(f"扫描目录: {args.input}")
        files = runner.scan_directory(args.input)
        print(f"找到 {len(files)} 个文件")

        if not files:
            print("未找到 SolidWorks 文件")
            return

        # 执行批量导出
        print(f"导出格式: {formats}")
        print(f"输出目录: {args.output}")
        results = exporter.batch_export(files, args.output, formats)

        # 打印结果
        print(f"\n导出完成!")
        print(f"  成功: {results['success']}")
        print(f"  失败: {results['failed']}")
        if results["errors"]:
            print("  错误详情:")
            for err in results["errors"]:
                print(f"    - {err}")

    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
