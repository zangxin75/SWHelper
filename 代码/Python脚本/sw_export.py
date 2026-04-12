"""
SolidWorks 文件导出模块
支持 STEP、IGES、STL、PDF、DXF、DWG、图片等格式导出
"""

import os
import logging
from typing import Optional
from sw_connection import SWConnection

logger = logging.getLogger(__name__)


class SWExport:
    """SolidWorks 文件导出器"""

    # SolidWorks 导出常量
    swSaveAsCurrentVersion = 0
    swSaveAsVersion_X = 2000

    def __init__(self, connection: SWConnection):
        self.conn = connection

    @property
    def app(self):
        return self.conn.app

    def export_step(self, filepath: str, version: str = "AP214") -> bool:
        """
        导出为 STEP 文件

        Args:
            filepath: 输出文件路径
            version: STEP 版本 (AP203/AP214/AP242)
        """
        model = self.conn.get_active_model()
        if model is None:
            raise RuntimeError("没有打开的文档")

        # 设置 STEP 导出选项
        step_map = {"AP203": 1, "AP214": 2, "AP242": 3}
        step_type = step_map.get(version, 2)

        self.app.SetUserPreferenceIntegerValue(186, step_type)  # swStepAP

        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 STEP ({version}): {filepath}")
        else:
            logger.error(f"STEP 导出失败: 错误码 {result}")
        return success

    def export_iges(self, filepath: str) -> bool:
        """导出为 IGES 文件"""
        model = self.conn.get_active_model()
        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 IGES: {filepath}")
        return success

    def export_stl(
        self,
        filepath: str,
        binary: bool = True,
        quality: int = 2,  # 0=粗糙, 1=良好, 2=精细
    ) -> bool:
        """
        导出为 STL 文件

        Args:
            filepath: 输出文件路径
            binary: True=二进制格式, False=ASCII格式
            quality: 网格质量 0=粗糙/1=良好/2=精细
        """
        model = self.conn.get_active_model()

        # 设置 STL 导出选项
        self.app.SetUserPreferenceIntegerValue(54, quality)  # stl 精度
        self.app.SetUserPreferenceToggle(55, binary)  # 二进制

        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 STL: {filepath}")
        return success

    def export_pdf(self, filepath: str) -> bool:
        """导出工程图为 PDF"""
        model = self.conn.get_active_model()
        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 PDF: {filepath}")
        return success

    def export_dxf(self, filepath: str) -> bool:
        """导出工程图为 DXF"""
        model = self.conn.get_active_model()
        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 DXF: {filepath}")
        return success

    def export_dwg(self, filepath: str) -> bool:
        """导出工程图为 DWG"""
        model = self.conn.get_active_model()
        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出 DWG: {filepath}")
        return success

    def export_image(
        self,
        filepath: str,
        width: int = 1920,
        height: int = 1080,
        format: str = "png",
    ) -> bool:
        """
        导出为图片

        Args:
            filepath: 输出文件路径
            width: 图片宽度
            height: 图片高度
            format: 图片格式 (png/jpg/tiff/bmp)
        """
        model = self.conn.get_active_model()

        # 设置图片大小
        self.app.SetUserPreferenceIntegerValue(163, width)
        self.app.SetUserPreferenceIntegerValue(164, height)

        result = model.SaveAs3(filepath, 0, 0)
        success = result == 0
        if success:
            logger.info(f"已导出图片: {filepath}")
        return success

    def batch_export(
        self,
        file_list: list,
        output_dir: str,
        formats: list = None,
    ) -> dict:
        """
        批量导出文件

        Args:
            file_list: 要导出的 SolidWorks 文件路径列表
            output_dir: 输出目录
            formats: 导出格式列表 ["step", "stl", "pdf"] 等

        Returns:
            导出结果统计 {"success": int, "failed": int, "errors": []}
        """
        if formats is None:
            formats = ["step"]

        results = {"success": 0, "failed": 0, "errors": []}

        format_exporters = {
            "step": self.export_step,
            "iges": self.export_iges,
            "stl": self.export_stl,
            "pdf": self.export_pdf,
            "dxf": self.export_dxf,
            "dwg": self.export_dwg,
        }

        os.makedirs(output_dir, exist_ok=True)

        for sw_file in file_list:
            try:
                self.conn.open_file(sw_file)
                base_name = os.path.splitext(os.path.basename(sw_file))[0]

                for fmt in formats:
                    exporter = format_exporters.get(fmt)
                    if exporter:
                        ext_map = {
                            "step": ".step", "iges": ".igs", "stl": ".stl",
                            "pdf": ".pdf", "dxf": ".dxf", "dwg": ".dwg",
                        }
                        out_path = os.path.join(
                            output_dir, base_name + ext_map.get(fmt, f".{fmt}")
                        )
                        if exporter(out_path):
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"{sw_file} -> {fmt}")

                self.conn.close_file(self.conn.get_active_model())

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{sw_file}: {str(e)}")
                logger.error(f"批量导出失败 {sw_file}: {e}")

        logger.info(
            f"批量导出完成: 成功={results['success']}, 失败={results['failed']}"
        )
        return results
