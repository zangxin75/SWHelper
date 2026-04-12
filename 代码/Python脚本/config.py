"""
SolidWorks 2026 自动化配置模块
管理 SolidWorks 安装路径、API 版本、导出格式等配置
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SWConfig:
    """SolidWorks 自动化配置"""

    # SolidWorks 安装路径（Windows 侧）
    sw_install_dir: str = r"D:\app_install\solidworks2026\SOLIDWORKS"

    # API 相关路径（WSL 侧访问 Windows 文件系统）
    sw_install_dir_wsl: str = "/mnt/d/app_install/solidworks2026/SOLIDWORKS"

    # SolidWorks 可执行文件
    sw_exe: str = r"D:\app_install\solidworks2026\SOLIDWORKS\sldworks.exe"

    # API 版本号（SolidWorks 2026 = 34）
    sw_api_version: int = 34

    # 默认文件保存路径
    default_save_dir: str = r"D:\sw2026_output"

    # 模板路径
    template_dir: str = r"D:\app_install\solidworks2026\SOLIDWORKS\templates"

    # 导出格式映射
    EXPORT_FORMATS: dict = field(default_factory=lambda: {
        "step": "step",
        "stp": "step",
        "iges": "iges",
        "igs": "iges",
        "stl": "stl",
        "pdf": "pdf",
        "dxf": "dxf",
        "dwg": "dwg",
        "eDrawing": "eDrawing",
        "tiff": "tiff",
        "jpg": "jpg",
        "png": "png",
    })

    # SolidWorks 文件扩展名映射
    FILE_TYPES: dict = field(default_factory=lambda: {
        "part": "sldprt",
        "assembly": "sldasm",
        "drawing": "slddrw",
    })

    # COM ProgID
    SW_PROGID: str = "SldWorks.Application"
    SW_DRAWING_PROGID: str = "SldWorks.DrawingDoc"

    # 默认单位：mm
    default_units: str = "mm"

    @property
    def api_help_path(self) -> str:
        return os.path.join(self.sw_install_dir_wsl, "api")

    @property
    def api_chm(self) -> str:
        return os.path.join(self.sw_install_dir_wsl, "api", "apihelp.chm")


# 全局配置单例
config = SWConfig()


def get_config() -> SWConfig:
    """获取全局配置"""
    return config


def update_config(**kwargs) -> SWConfig:
    """更新配置参数"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
