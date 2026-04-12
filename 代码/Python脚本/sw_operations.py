"""
SolidWorks 建模操作封装模块
提供常用建模操作的 Python 封装，通过 COM API 驱动 SolidWorks

使用方式：
    from sw_connection import SWConnection
    from sw_operations import SWOperations

    conn = SWConnection()
    conn.connect()
    ops = SWOperations(conn)

    # 创建一个圆柱体零件
    ops.create_cylinder(radius=25, height=50)
"""

import logging
from typing import Optional, Tuple
from sw_connection import SWConnection

logger = logging.getLogger(__name__)


class SWOperations:
    """SolidWorks 建模操作封装"""

    # SolidWorks 常量
    swSelSKETCHES = 8
    swSelSKETCHSEGS = 25
    swSelFACES = 2
    swSelEDGES = 1
    swMateCOINCIDENT = 0
    swMateCONCENTRIC = 1
    swMateDISTANCE = 5
    swDocPART = 1
    swDocASSEMBLY = 2
    swDocDRAWING = 3

    def __init__(self, connection: SWConnection):
        self.conn = connection

    @property
    def app(self):
        return self.conn.app

    def new_part(self) -> object:
        """创建新零件文档"""
        return self.app.NewPart()

    def new_assembly(self) -> object:
        """创建新装配体文档"""
        return self.app.NewAssembly()

    def new_drawing(self) -> object:
        """创建新工程图文档"""
        return self.app.NewDrawing()

    def select_by_id(self, name: str, type_flag: int) -> bool:
        """通过名称选择对象"""
        model = self.conn.get_active_model()
        return model.Extension.SelectByID2(
            name,  # 名称
            self._type_to_string(type_flag),  # 类型字符串
            0, 0, 0,  # x, y, z 坐标
            False,  # 追加选择
            0,  # 标记
            None,  # callout
        )

    def create_sketch_on_plane(self, plane_name: str = "前视基准面"):
        """
        在指定基准面上创建草图

        Args:
            plane_name: 基准面名称（前视基准面/上视基准面/右视基准面）
        """
        model = self.conn.get_active_model()
        # 选择基准面
        model.Extension.SelectByID2(
            plane_name, "PLANE", 0, 0, 0, False, 0, None, 0
        )
        # 进入草图模式
        model.SketchManager.InsertSketch(True)
        logger.info(f"已在 {plane_name} 上创建草图")

    def insert_sketch(self):
        """退出/完成当前草图"""
        model = self.conn.get_active_model()
        model.SketchManager.InsertSketch(True)

    def create_line(self, x1: float, y1: float, x2: float, y2: float) -> object:
        """创建直线草图段"""
        model = self.conn.get_active_model()
        sketch_seg = model.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)
        return sketch_seg

    def create_circle(self, cx: float, cy: float, radius: float) -> object:
        """创建圆草图"""
        model = self.conn.get_active_model()
        sketch_seg = model.SketchManager.CreateCircle(
            cx, cy, 0, cx + radius, cy, 0
        )
        return sketch_seg

    def create_rectangle(self, x1: float, y1: float, x2: float, y2: float) -> object:
        """创建矩形草图"""
        model = self.conn.get_active_model()
        sketch_seg = model.SketchManager.CreateCornerRectangle(
            x1, y1, 0, x2, y2, 0
        )
        return sketch_seg

    def create_arc(
        self, cx: float, cy: float, radius: float, start_angle: float, end_angle: float
    ) -> object:
        """创建圆弧草图"""
        model = self.conn.get_active_model()
        import math
        sx = cx + radius * math.cos(start_angle)
        sy = cy + radius * math.sin(start_angle)
        ex = cx + radius * math.cos(end_angle)
        ey = cy + radius * math.sin(end_angle)
        sketch_seg = model.SketchManager.CreateArc(
            cx, cy, 0, sx, sy, 0, ex, ey, 0, 1  # 1 = 逆时针
        )
        return sketch_seg

    def extrude(self, depth: float, direction: int = 1, merge: bool = True) -> object:
        """
        拉伸凸台

        Args:
            depth: 拉伸深度（mm）
            direction: 1=正向, 2=反向, 6=双向对称
            merge: 是否合并结果
        """
        model = self.conn.get_active_model()
        feature = model.FeatureManager.FeatureExtrusion2(
            True,  # sd
            False,  # flip
            direction,  # dir
            0,  # type (swBlind = 0)
            0,  # type2
            depth,  # depth1
            0,  # depth2
            False,  # draftWhileExtruding
            0,  # draftAngle
            False,  # draftOutward
            merge,  # merge
            False,  # useFeatScope
            False,  # useAutoSelect
            0,  # assembly feature scope options
            False,  # auto select components
            True,  # propagate
        )
        logger.info(f"拉伸凸台: 深度={depth}mm")
        return feature

    def cut_extrude(self, depth: float, direction: int = 1) -> object:
        """拉伸切除"""
        model = self.conn.get_active_model()
        feature = model.FeatureManager.FeatureExtrusion2(
            True,  # sd
            False,  # flip
            direction,  # dir
            0,  # type (swBlind)
            0,  # type2
            depth,  # depth1
            0,  # depth2
            False, False, False,  # draft params
            False,  # merge (cut = false)
            False, False,
            0, False, True,
        )
        logger.info(f"拉伸切除: 深度={depth}mm")
        return feature

    def revolve(self, angle: float = 360.0, axis_name: str = None) -> object:
        """
        旋转凸台

        Args:
            angle: 旋转角度（度）
            axis_name: 旋转轴名称（None 则使用草图中的中心线）
        """
        model = self.conn.get_active_model()
        if axis_name:
            model.Extension.SelectByID2(axis_name, "AXIS", 0, 0, 0, True, 0, None, 0)

        feature = model.FeatureManager.FeatureRevolve2(
            angle,  # angle
            False,  # reverse
            0,  # type
            0,  # type2
            0,  # depth
            0,  # depth2
            False, False, False,
            False, False, False,
            0, False,
        )
        logger.info(f"旋转凸台: 角度={angle}°")
        return feature

    def create_cylinder(self, radius: float = 25, height: float = 50, plane: str = "前视基准面"):
        """
        创建圆柱体零件（快速方法）

        Args:
            radius: 半径（mm）
            height: 高度（mm）
            plane: 草图基准面
        """
        model = self.conn.get_active_model()
        if model is None:
            self.new_part()
            model = self.conn.get_active_model()

        # 选择基准面并创建草图
        model.Extension.SelectByID2(plane, "PLANE", 0, 0, 0, False, 0, None, 0)
        model.SketchManager.InsertSketch(True)

        # 绘制圆
        model.SketchManager.CreateCircle(0, 0, 0, radius, 0, 0)

        # 退出草图
        model.SketchManager.InsertSketch(True)

        # 拉伸
        self.extrude(height)
        logger.info(f"创建圆柱体: R={radius}mm, H={height}mm")

    def create_box(self, length: float, width: float, height: float, plane: str = "前视基准面"):
        """
        创建长方体零件（快速方法）

        Args:
            length: 长度（mm）
            width: 宽度（mm）
            height: 高度（mm）
            plane: 草图基准面
        """
        model = self.conn.get_active_model()
        if model is None:
            self.new_part()
            model = self.conn.get_active_model()

        # 选择基准面并创建草图
        model.Extension.SelectByID2(plane, "PLANE", 0, 0, 0, False, 0, None, 0)
        model.SketchManager.InsertSketch(True)

        # 绘制矩形
        model.SketchManager.CreateCornerRectangle(
            -length / 2, -width / 2, 0, length / 2, width / 2, 0
        )

        # 退出草图
        model.SketchManager.InsertSketch(True)

        # 拉伸
        self.extrude(height)
        logger.info(f"创建长方体: {length}x{width}x{height}mm")

    def add_fillet(self, radius: float, edges: list = None) -> object:
        """添加圆角"""
        model = self.conn.get_active_model()
        feature = model.FeatureManager.FeatureFillett(
            radius,  # radius
            1,  # fillet type (swFilletTypeSimple)
            False,  # propagate
            edges if edges else [],
            0,  # options
        )
        logger.info(f"添加圆角: R={radius}mm")
        return feature

    def add_chamfer(self, distance: float, angle: float = 45) -> object:
        """添加倒角"""
        model = self.conn.get_active_model()
        feature = model.FeatureManager.InsertChamfer2(
            2,  # type (swChamferAngleDist)
            distance,  # width
            angle,  # angle
            False, False, False, False,  # options
        )
        logger.info(f"添加倒角: {distance}mm x {angle}°")
        return feature

    def save_file(self, filepath: str = None) -> bool:
        """
        保存当前文件

        Args:
            filepath: 保存路径（None 则保存到原路径）
        """
        model = self.conn.get_active_model()
        if filepath:
            result = model.SaveAs3(filepath, 0, 0)
        else:
            result = model.Save()
        logger.info(f"保存文件: {filepath or '原路径'}")
        return result == 0

    def _type_to_string(self, type_flag: int) -> str:
        """将选择类型常量转换为 SolidWorks 类型字符串"""
        type_map = {
            1: "EDGE",
            2: "FACE",
            8: "SKETCH",
            25: "SKETCHSEGMENT",
        }
        return type_map.get(type_flag, "")
