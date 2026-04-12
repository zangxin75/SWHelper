"""
SolidWorks 批处理执行器
支持批量操作、参数化设计、定时任务等
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Callable, Optional
from sw_connection import SWConnection
from config import get_config

logger = logging.getLogger(__name__)


class BatchRunner:
    """SolidWorks 批处理执行器"""

    def __init__(self, connection: SWConnection = None):
        self.config = get_config()
        self._conn = connection

    @property
    def conn(self) -> SWConnection:
        if self._conn is None:
            self._conn = SWConnection(self.config)
            self._conn.connect(startup=True)
        return self._conn

    def run_on_files(
        self,
        file_list: list,
        operation: Callable,
        save: bool = True,
        close_after: bool = True,
    ) -> list:
        """
        对文件列表中的每个文件执行指定操作

        Args:
            file_list: SolidWorks 文件路径列表
            operation: 操作函数，接收 model 对象作为参数
            save: 操作后是否保存
            close_after: 操作后是否关闭文件

        Returns:
            操作结果列表
        """
        results = []

        for filepath in file_list:
            try:
                logger.info(f"处理文件: {filepath}")
                model = self.conn.open_file(filepath)
                result = operation(model)
                results.append({"file": filepath, "status": "success", "result": result})

                if save:
                    model.Save()
                if close_after:
                    self.conn.close_file(model)

            except Exception as e:
                logger.error(f"处理失败 {filepath}: {e}")
                results.append({"file": filepath, "status": "error", "error": str(e)})

        return results

    def scan_directory(self, directory: str, extensions: list = None) -> list:
        """
        扫描目录中的 SolidWorks 文件

        Args:
            directory: 扫描目录（Windows 路径）
            extensions: 文件扩展名列表，默认 [".sldprt", ".sldasm", ".slddrw"]

        Returns:
            文件路径列表
        """
        if extensions is None:
            extensions = [".sldprt", ".sldasm", ".slddrw"]

        found_files = []
        for ext in extensions:
            pattern = f"**/*{ext}"
            # 通过 WSL 路径扫描
            wsl_dir = directory.replace("D:\\", "/mnt/d/").replace("C:\\", "/mnt/c/")
            wsl_dir = wsl_dir.replace("\\", "/")
            for p in Path(wsl_dir).rglob(f"*{ext}"):
                # 转回 Windows 路径
                win_path = str(p).replace("/mnt/d/", "D:\\").replace("/mnt/c/", "C:\\")
                win_path = win_path.replace("/", "\\")
                found_files.append(win_path)

        logger.info(f"扫描到 {len(found_files)} 个文件")
        return found_files

    def run_parameterized(
        self,
        template_path: str,
        parameters: list,
        output_dir: str,
        naming_func: Optional[Callable] = None,
    ) -> list:
        """
        参数化批量生成零件

        Args:
            template_path: 模板零件路径
            parameters: 参数字典列表 [{"d1": 10, "d2": 20}, ...]
            output_dir: 输出目录
            naming_func: 文件命名函数，接收参数字典返回文件名

        Returns:
            生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)
        generated = []

        for i, params in enumerate(parameters):
            try:
                model = self.conn.open_file(template_path)

                # 修改参数
                dim_manager = model.Parameter("")
                for name, value in params.items():
                    dim = model.Parameter(name)
                    if dim:
                        dim.SetSystemValue3(value, 0, [])
                    else:
                        logger.warning(f"参数未找到: {name}")

                # 重建模型
                model.EditRebuild3()

                # 生成文件名
                if naming_func:
                    filename = naming_func(params)
                else:
                    filename = f"part_{i+1:04d}.sldprt"

                out_path = os.path.join(output_dir, filename)
                model.SaveAs3(out_path, 0, 0)
                generated.append(out_path)

                self.conn.close_file(model)
                logger.info(f"已生成: {out_path}")

            except Exception as e:
                logger.error(f"参数化生成失败 (参数集 {i+1}): {e}")

        return generated

    def load_task_config(self, config_path: str) -> dict:
        """从 JSON 文件加载任务配置"""
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_from_config(self, config_path: str) -> list:
        """
        从 JSON 配置文件运行批量任务

        配置文件格式示例：
        {
            "files": ["D:\\parts\\part1.sldprt", ...],
            "operations": [
                {"type": "export", "format": "step", "output_dir": "D:\\output"},
                {"type": "export", "format": "stl", "output_dir": "D:\\output"}
            ]
        }
        """
        config = self.load_task_config(config_path)
        results = []

        files = config.get("files", [])
        if config.get("scan_directory"):
            files.extend(
                self.scan_directory(config["scan_directory"], config.get("extensions"))
            )

        for op_config in config.get("operations", []):
            op_type = op_config.get("type")
            if op_type == "export":
                from sw_export import SWExport
                exporter = SWExport(self.conn)
                result = exporter.batch_export(
                    files,
                    op_config.get("output_dir", "D:\\sw2026_output"),
                    op_config.get("formats", ["step"]),
                )
                results.append(result)

        return results
