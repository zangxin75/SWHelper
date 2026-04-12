"""
SolidWorks 工程图自动化模块
自动从 3D 模型生成工程图、添加视图、标注尺寸
"""

import logging
from typing import Optional
from sw_connection import SWConnection

logger = logging.getLogger(__name__)


class SWDrawing:
    """SolidWorks 工程图自动化"""

    # 视图类型常量
    swDrawingViewNormal = 0
    swDrawingViewSection = 1
    swDrawingViewDetail = 2
    swDrawingViewProjected = 3
    swDrawingViewAuxiliary = 4

    # 尺寸类型
    swDimensionTypeLinear = 0
    swDimensionTypeDiameter = 1
    swDimensionTypeRadial = 2
    swDimensionTypeAngular = 3

    def __init__(self, connection: SWConnection):
        self.conn = connection

    @property
    def app(self):
        return self.conn.app

    def create_drawing_from_part(
        self,
        part_path: str,
        template: str = None,
        paper_size: int = 5,  # swDwgPapersA3
        scale_num: float = 1.0,
        scale_den: float = 1.0,
    ) -> object:
        """
        从零件创建工程图

        Args:
            part_path: 零件文件路径
            template: 工程图模板路径（None 使用默认模板）
            paper_size: 图纸大小常量
            scale_num: 比例分子
            scale_den: 比例分母

        Returns:
            DrawingDoc COM 对象
        """
        # 打开零件
        part = self.conn.open_file(part_path)

        # 创建工程图
        if template:
            drawing = self.app.NewDocument(template, paper_size, 0.2794, 0.2159)
        else:
            drawing = self.app.NewDrawing()

        if drawing is None:
            raise RuntimeError("无法创建工程图文档")

        logger.info(f"已从零件创建工程图: {part_path}")
        return drawing

    def add_standard_views(
        self,
        model_path: str,
        position_x: float = 0.1,
        position_y: float = 0.2,
    ) -> dict:
        """
        添加标准三视图（主视图、俯视图、左视图）

        Args:
            model_path: 模型文件路径
            position_x: 主视图 X 位置
            position_y: 主视图 Y 位置

        Returns:
            包含三个视图对象的字典
        """
        model = self.conn.get_active_model()
        views = {}

        # 创建主视图（前视）
        views["front"] = model.CreateDrawViewFromModelView3(
            model_path, "*前视", position_x, position_y, 0
        )

        # 创建俯视图
        views["top"] = model.CreateDrawViewFromModelView3(
            model_path, "*上视", position_x, position_y + 0.15, 0
        )

        # 创建右视图
        views["right"] = model.CreateDrawViewFromModelView3(
            model_path, "*右视", position_x + 0.2, position_y, 0
        )

        logger.info("已添加标准三视图")
        return views

    def add_isometric_view(
        self,
        model_path: str,
        position_x: float = 0.35,
        position_y: float = 0.35,
    ) -> object:
        """添加等轴测视图"""
        model = self.conn.get_active_model()
        view = model.CreateDrawViewFromModelView3(
            model_path, "*等轴测", position_x, position_y, 0
        )
        logger.info("已添加等轴测视图")
        return view

    def add_section_view(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
    ) -> object:
        """
        添加剖视图

        Args:
            start_x, start_y: 剖面线起点
            end_x, end_y: 剖面线终点
        """
        model = self.conn.get_active_model()
        view = model.CreateSectionViewAt5(
            start_x, start_y, 0,
            end_x, end_y, 0,
            "",  # label
            0,  # options
        )
        logger.info("已添加剖视图")
        return view

    def add_title_block_info(
        self,
        part_number: str = "",
        description: str = "",
        material: str = "",
        drawn_by: str = "",
        date: str = "",
        scale: str = "1:1",
    ):
        """
        填写标题栏信息

        Args:
            part_number: 零件编号
            description: 描述
            material: 材料
            drawn_by: 制图人
            date: 日期
            scale: 比例
        """
        model = self.conn.get_active_model()

        # 设置自定义属性
        properties = {
            "零件编号": part_number,
            "描述": description,
            "材料": material,
            "制图": drawn_by,
            "日期": date,
            "比例": scale,
        }

        for prop_name, prop_value in properties.items():
            if prop_value:
                model.Extension.CustomPropertyManager("").Set2(
                    prop_name, prop_value
                )

        logger.info(f"已填写标题栏: {part_number}")

    def auto_dimension(self, view: object = None):
        """
        自动添加尺寸标注（利用 SolidWorks 2026 AI 辅助）

        注意：此功能需要 SolidWorks 2026 的 AI 自动出图支持
        """
        model = self.conn.get_active_model()

        # 使用 SolidWorks 2026 的自动插入尺寸功能
        # swAutoInsertDimensionsType_All = 3
        model.Extension.AutoDimension(
            3,  # dimension type
            0,  # scheme type
        )
        logger.info("已执行自动尺寸标注")

    def set_sheet_scale(self, numerator: float, denominator: float):
        """设置图纸比例"""
        model = self.conn.get_active_model()
        sheet = model.GetCurrentSheet()
        sheet.SetScale(numerator, denominator)
        logger.info(f"图纸比例已设为 {numerator}:{denominator}")

    def set_sheet_size(self, width: float, height: float):
        """设置图纸尺寸"""
        model = self.conn.get_active_model()
        sheet = model.GetCurrentSheet()
        sheet.SetSize2(width, height)
        logger.info(f"图纸尺寸已设为 {width}x{height}")
