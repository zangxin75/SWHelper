#!/usr/bin/env python3
"""
示例：参数化零件生成
通过修改参数批量生成不同尺寸的法兰零件

使用方式：
    在 Windows 环境下运行（或通过 WSL 调用 Windows Python）：
    python parametric_part.py

要求：SolidWorks 2026 已启动
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sw_connection import SWConnection
from sw_operations import SWOperations
from sw_export import SWExport


def create_flange(conn: SWConnection, params: dict) -> str:
    """
    创建法兰零件

    Args:
        conn: SolidWorks 连接
        params: 法兰参数字典
            - outer_d: 外径
            - inner_d: 内径
            - thickness: 厚度
            - bolt_circle_d: 螺栓孔分布圆直径
            - bolt_hole_d: 螺栓孔直径
            - bolt_count: 螺栓孔数量

    Returns:
        保存的文件路径
    """
    ops = SWOperations(conn)
    app = conn.app

    # 创建新零件
    ops.new_part()
    model = conn.get_active_model()

    # 提取参数（单位：mm）
    outer_r = params["outer_d"] / 2
    inner_r = params["inner_d"] / 2
    thickness = params["thickness"]
    bolt_circle_r = params["bolt_circle_d"] / 2
    bolt_hole_r = params["bolt_hole_d"] / 2
    bolt_count = params["bolt_count"]

    # 1. 在前视基准面创建草图
    ops.create_sketch_on_plane("前视基准面")

    # 2. 绘制外圆
    ops.create_circle(0, 0, outer_r)

    # 3. 退出草图并拉伸
    ops.insert_sketch()
    ops.extrude(thickness)

    # 4. 选择上表面创建草图（用于切除内孔）
    model.Extension.SelectByID2("", "FACE", 0, 0, thickness, False, 0, None, 0)
    model.SketchManager.InsertSketch(True)

    # 5. 绘制内圆
    ops.create_circle(0, 0, inner_r)
    ops.insert_sketch()

    # 6. 切除拉伸内孔
    ops.cut_extrude(thickness)

    # 7. 添加螺栓孔（通过阵列）
    # 在上表面创建草图
    model.Extension.SelectByID2("", "FACE", 0, 0, thickness, False, 0, None, 0)
    model.SketchManager.InsertSketch(True)

    # 绘制第一个螺栓孔
    import math
    ops.create_circle(bolt_circle_r, 0, bolt_hole_r)
    ops.insert_sketch()

    # 切除第一个螺栓孔
    ops.cut_extrude(thickness)

    # 8. 圆周阵列螺栓孔
    # 选择切除特征
    model.Extension.SelectByID2("切除-拉伸2", "BODYFEATURE", 0, 0, 0, False, 0, None, 0)
    # 选择临时轴作为阵列轴
    model.Extension.SelectByID2("", "AXIS", 0, 0, 0, True, 0, None, 0)

    # 创建圆周阵列
    feature = model.FeatureManager.FeatureCircularPattern2(
        bolt_count,  # 实例数
        2 * math.pi,  # 总角度（弧度）
        False,  # 反向
        "",  # 对称
    )

    # 9. 保存文件
    output_dir = params.get("output_dir", r"D:\sw2026_output")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"flange_{params['outer_d']}x{params['inner_d']}x{params['thickness']}.sldprt"
    filepath = os.path.join(output_dir, filename)
    ops.save_file(filepath)

    return filepath


def main():
    """批量生成不同规格的法兰"""
    # 法兰参数表
    flange_specs = [
        {
            "name": "DN50",
            "outer_d": 140, "inner_d": 50, "thickness": 16,
            "bolt_circle_d": 105, "bolt_hole_d": 12, "bolt_count": 4,
        },
        {
            "name": "DN80",
            "outer_d": 185, "inner_d": 80, "thickness": 20,
            "bolt_circle_d": 145, "bolt_hole_d": 16, "bolt_count": 4,
        },
        {
            "name": "DN100",
            "outer_d": 210, "inner_d": 100, "thickness": 22,
            "bolt_circle_d": 170, "bolt_hole_d": 16, "bolt_count": 4,
        },
        {
            "name": "DN150",
            "outer_d": 265, "inner_d": 150, "thickness": 24,
            "bolt_circle_d": 220, "bolt_hole_d": 18, "bolt_count": 8,
        },
    ]

    conn = SWConnection()
    conn.connect(startup=True)

    try:
        for spec in flange_specs:
            print(f"\n正在生成法兰 {spec['name']}...")
            filepath = create_flange(conn, spec)
            print(f"  已保存: {filepath}")

        print(f"\n全部完成! 共生成 {len(flange_specs)} 个法兰零件")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
