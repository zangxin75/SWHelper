"""
SolidWorks COM 连接管理模块
负责建立、管理和释放与 SolidWorks 的 COM 连接

重要：此模块必须在 Windows 环境下运行（通过 WSL 调用 Windows Python）
或直接在 Windows Python 环境中运行。
"""

import os
import time
import logging
from typing import Optional, Any

from config import SWConfig, get_config

logger = logging.getLogger(__name__)


class SWConnection:
    """SolidWorks COM 连接管理器"""

    def __init__(self, config: Optional[SWConfig] = None):
        self.config = config or get_config()
        self._sw_app: Optional[Any] = None
        self._connected = False

    def connect(self, visible: bool = True, startup: bool = False) -> Any:
        """
        连接到 SolidWorks 实例

        Args:
            visible: 是否显示 SolidWorks 窗口
            startup: 如果没有运行实例，是否启动新的

        Returns:
            SolidWorks Application COM 对象
        """
        try:
            import win32com.client
        except ImportError:
            raise ImportError(
                "需要安装 pywin32: pip install pywin32\n"
                "注意：此模块需要在 Windows 环境下运行"
            )

        try:
            # 尝试连接到已运行的 SolidWorks 实例
            self._sw_app = win32com.client.GetActiveObject(
                self.config.SW_PROGID
            )
            logger.info("已连接到运行中的 SolidWorks 实例")
        except Exception:
            if startup:
                # 启动新的 SolidWorks 实例
                self._sw_app = win32com.client.Dispatch(
                    self.config.SW_PROGID
                )
                logger.info("已启动新的 SolidWorks 实例")
            else:
                raise ConnectionError(
                    "未找到运行中的 SolidWorks 实例。"
                    "请先启动 SolidWorks 或设置 startup=True"
                )

        # 设置可见性
        if self._sw_app:
            self._sw_app.Visible = visible
            self._connected = True

        return self._sw_app

    @property
    def app(self) -> Any:
        """获取 SolidWorks Application 对象"""
        if not self._connected or self._sw_app is None:
            raise RuntimeError("未连接到 SolidWorks，请先调用 connect()")
        return self._sw_app

    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        if not self._connected:
            return False
        try:
            # 尝试访问属性来验证连接仍然有效
            _ = self._sw_app.Visible
            return True
        except Exception:
            self._connected = False
            return False

    def get_active_model(self) -> Any:
        """获取当前活动文档"""
        return self.app.ActiveDoc

    def get_model_type(self, model: Any) -> str:
        """
        获取文档类型

        Returns:
            "part" | "assembly" | "drawing" | "none"
        """
        if model is None:
            return "none"
        sw_type = model.GetType()
        type_map = {1: "part", 2: "assembly", 3: "drawing"}
        return type_map.get(sw_type, "unknown")

    def open_file(self, filepath: str, readonly: bool = False) -> Any:
        """
        打开 SolidWorks 文件

        Args:
            filepath: 文件路径（Windows 格式）
            readonly: 是否只读打开

        Returns:
            ModelDoc2 COM 对象
        """
        errors = 0
        warnings = 0
        open_options = 1 if readonly else 0  # swOpenDocOptions_ReadOnly

        model = self.app.OpenDoc6(
            filepath,
            self._get_doc_type_from_ext(filepath),
            open_options,
            "",  # configuration
        )

        if model is None:
            raise RuntimeError(f"无法打开文件: {filepath}")

        logger.info(f"已打开文件: {filepath}")
        return model

    def close_file(self, model: Any, save: bool = False) -> None:
        """关闭文档"""
        if save:
            model.Save()
        self.app.CloseDoc(model.GetPathName())

    def _get_doc_type_from_ext(self, filepath: str) -> int:
        """根据文件扩展名返回 SolidWorks 文档类型常量"""
        ext = os.path.splitext(filepath)[1].lower()
        type_map = {
            ".sldprt": 1,  # swDocPART
            ".prt": 1,
            ".sldasm": 2,  # swDocASSEMBLY
            ".asm": 2,
            ".slddrw": 3,  # swDocDRAWING
            ".drw": 3,
        }
        return type_map.get(ext, 1)

    def disconnect(self):
        """断开连接（不关闭 SolidWorks）"""
        self._sw_app = None
        self._connected = False
        logger.info("已断开 SolidWorks 连接")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
