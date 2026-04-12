# -*- coding: utf-8 -*-
"""
SW2026 可靠 COM 自动化连接模块
基于全网搜索结果整合的最佳实践

关键发现来源:
- pywin32 GitHub Issue #622: dynamic dispatch by-ref 参数问题
- StackOverflow: SelectByID2 Callout 参数类型不匹配
- Joshua Redstone Blog: VARIANT 类型封装方法
- SolidWorks 官方 API 文档 2026
"""
import pythoncom
pythoncom.CoInitialize()

import win32com.client
import win32com.client.gencache as gencache
import pythoncom
import pywintypes
import math
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger('sw_auto')


class SWConnection:
    """SolidWorks COM 连接管理器 - SW2026 兼容"""

    def __init__(self, use_early_binding=False):
        """
        连接到运行中的 SolidWorks 实例

        Args:
            use_early_binding: 是否尝试早期绑定 (gencache.EnsureDispatch)
                             早期绑定性能更好，但 SW 某些版本不支持
        """
        self.use_early_binding = use_early_binding
        self.swApp = None
        self.swModel = None
        self.skMgr = None
        self.selMgr = None
        self.featMgr = None

        self._connect()

    def _connect(self):
        """连接到 SolidWorks，自动降级"""
        try:
            if self.use_early_binding:
                log.info("尝试早期绑定 (EnsureDispatch)...")
                self.swApp = gencache.EnsureDispatch('SldWorks.Application')
                log.info("早期绑定成功")
            else:
                raise Exception("跳过，使用动态绑定")
        except Exception as e:
            log.info(f"使用动态绑定 (dynamic.Dispatch): {e}")
            self.swApp = win32com.client.dynamic.Dispatch('SldWorks.Application')

        if not self.swApp:
            raise ConnectionError("无法连接到 SolidWorks")

        self._refresh_doc_refs()
        log.info("SolidWorks 连接成功")

    def _refresh_doc_refs(self):
        """刷新当前文档的引用"""
        self.swModel = self.swApp.ActiveDoc
        if self.swModel:
            self.skMgr = self.swModel.SketchManager
            self.selMgr = self.swModel.SelectionManager
            self.featMgr = self.swModel.FeatureManager
        else:
            self.skMgr = None
            self.selMgr = None
            self.featMgr = None

    # ================================================================
    #  文档操作 - 修复了 OpenDoc6 / NewDocument / SaveAs 的类型问题
    # ================================================================

    def open_doc(self, path, doc_type=1):
        """
        打开 SolidWorks 文件 (兼容 SW2026)

        Args:
            path: 文件路径 (Windows 格式)
            doc_type: 1=Part, 2=Assembly, 3=Drawing

        核心修复: OpenDoc6 的 Errors/Warnings 是 [out] long* 参数
        必须用 VARIANT(VT_BYREF | VT_I4) 包装
        """
        # 方法1: 简单 OpenDoc (推荐，无 by-ref 参数)
        try:
            doc = self.swApp.OpenDoc(path, doc_type)
            if doc:
                self._refresh_doc_refs()
                log.info(f"OpenDoc 成功: {path}")
                return doc
        except Exception as e:
            log.warning(f"OpenDoc 失败: {e}")

        # 方法2: OpenDoc6 + VARIANT 包装 by-ref 参数
        try:
            errors = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = win32com.client.VARIANT(
                pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            doc = self.swApp.OpenDoc6(
                path, doc_type, 0, "", errors, warnings)
            if doc:
                self._refresh_doc_refs()
                log.info(f"OpenDoc6 成功: {path}")
                return doc
        except Exception as e:
            log.warning(f"OpenDoc6 也失败: {e}")

        raise IOError(f"无法打开文件: {path}")

    def new_part(self):
        """
        创建新零件文档 (兼容 SW2026)

        核心修复: NewDocument 在 SW2026 dynamic dispatch 中失效
        使用 swApp.NewPart 属性调用替代
        """
        # 方法1: NewPart 属性 (SW2026 最可靠)
        try:
            self.swApp.NewPart
            self._refresh_doc_refs()
            if self.swModel:
                log.info("NewPart 创建成功")
                return self.swModel
        except Exception as e:
            log.warning(f"NewPart 失败: {e}")

        # 方法2: NewDocument + GetDocumentTemplate
        try:
            template = self.swApp.GetDocumentTemplate(1, "", 0, 0, 0)
            if template:
                self.swApp.NewDocument(template, 0, 0, 0)
                self._refresh_doc_refs()
                if self.swModel:
                    log.info("NewDocument 创建成功")
                    return self.swModel
        except Exception as e:
            log.warning(f"NewDocument 失败: {e}")

        raise RuntimeError("无法创建新零件文档")

    def save_as(self, path, overwrite=False):
        """
        保存文件 (兼容 SW2026)

        核心修复: SaveAs3/SaveAs4 参数错误，使用 SaveAs2
        """
        try:
            result = self.swModel.SaveAs2(path, 0, overwrite, True)
            log.info(f"SaveAs2 成功: {path}")
            return result == 0
        except Exception as e:
            log.error(f"保存失败: {e}")
            return False

    def save(self):
        """保存当前文档"""
        try:
            result = self.swModel.Save()
            return True
        except:
            return False

    def close_doc(self, path=None):
        """
        关闭文档 (兼容 SW2026)

        注意: swModel.Close() 在动态调度中不可用
        必须用 swApp.CloseDoc(path) 或 swApp.CloseAllDocuments
        """
        try:
            if path:
                self.swApp.CloseDoc(path)
            else:
                self.swApp.CloseAllDocuments
            self._refresh_doc_refs()
            return True
        except Exception as e:
            log.warning(f"关闭文档失败: {e}")
            return False

    # ================================================================
    #  选择操作 - 修复了 SelectByID2 / SelectByRay 的类型问题
    # ================================================================

    def select_by_id(self, name, type_str, x=0, y=0, z=0,
                     append=False, mark=0, select_option=0):
        """
        按名称选择对象 (兼容 SW2026)

        核心修复: SelectByID2 的 Callout 参数是 IDispatch* 类型
        必须用 VARIANT(VT_DISPATCH, None) 包装，不能直接传 None

        注意: 中文版 SW 的名称是中文 (如 "上视基准面" 而非 "Top Plane")
        对于平面选择，推荐使用 select_plane() 方法更可靠
        """
        callout = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
        return self.swModel.Extension.SelectByID2(
            name, type_str, x, y, z, append, mark, callout, select_option)

    def select_plane(self, plane_name):
        """
        选择参考平面 (推荐方法)

        比 SelectByID2 更可靠: FeatureByName + Select2
        """
        try:
            feat = self.swModel.FeatureByName(plane_name)
            if feat:
                feat.Select2(False, 0)
                log.info(f"选择平面: {plane_name}")
                return True
        except:
            pass

        # 降级方案: 遍历特征查找
        feats = self.featMgr.GetFeatures(False)
        for f in feats:
            if f.GetTypeName == 'RefPlane' and plane_name in f.Name:
                f.Select2(False, 0)
                log.info(f"选择平面 (遍历): {f.Name}")
                return True
        return False

    def select_top_face(self, feature):
        """选择特征的顶面 (法线 Y > 0)"""
        faces = feature.GetFaces
        for face in faces:
            normal = face.Normal
            if normal[1] > 0.9:
                face.Select4(False, self.selMgr.CreateSelectData)
                return True
        return False

    def select_bottom_face(self, feature):
        """选择特征的底面 (法线 Y < 0)"""
        faces = feature.GetFaces
        for face in faces:
            normal = face.Normal
            if normal[1] < -0.9:
                face.Select4(False, self.selMgr.CreateSelectData)
                return True
        return False

    # ================================================================
    #  特征操作
    # ================================================================

    def enter_sketch(self, plane_name='上视基准面'):
        """在指定平面上进入草图模式"""
        self.select_plane(plane_name)
        self.swModel.InsertSketch2(True)

    def exit_sketch(self):
        """退出草图模式"""
        self.swModel.InsertSketch2(True)

    def boss_extrude(self, depth_mm):
        """
        凸台拉伸

        Args:
            depth_mm: 深度 (毫米)

        Note: FeatureExtrusion2 的深度参数单位是米
        """
        d = depth_mm / 1000.0
        return self.featMgr.FeatureExtrusion2(
            True, False, False, 0, 0, d, d,
            False, False, False, False, 0.0, 0.0,
            False, False, False, False,
            True, True, True, 0, 0, False)

    def cut_extrude(self, depth_mm, through_all=False):
        """
        切除拉伸

        Args:
            depth_mm: 深度 (毫米)
            through_all: 是否贯穿所有
        """
        d = depth_mm / 1000.0
        t1 = 1 if through_all else 0
        return self.featMgr.FeatureExtrusion2(
            True, True, False, t1, 0, d, d,
            False, False, False, False, 0.0, 0.0,
            False, False, False, False,
            True, True, True, 0, 0, False)

    def sketch_rectangle(self, x1_mm, y1_mm, x2_mm, y2_mm):
        """创建矩形草图 (毫米单位)"""
        return self.skMgr.CreateCornerRectangle(
            x1_mm / 1000.0, y1_mm / 1000.0, 0,
            x2_mm / 1000.0, y2_mm / 1000.0, 0)

    def sketch_circle(self, cx_mm, cy_mm, r_mm):
        """创建圆形草图 (毫米单位)"""
        return self.skMgr.CreateCircleByRadius(
            cx_mm / 1000.0, cy_mm / 1000.0, 0,
            r_mm / 1000.0)

    # ================================================================
    #  特征查找工具
    # ================================================================

    def get_planes(self):
        """获取所有参考平面"""
        feats = self.featMgr.GetFeatures(False)
        return [f for f in feats if f.GetTypeName == 'RefPlane']

    def find_features(self, type_name):
        """按类型查找特征"""
        feats = self.featMgr.GetFeatures(False)
        return [f for f in feats if f.GetTypeName == type_name]

    def find_last_sketch(self):
        """查找最后一个草图"""
        sketches = self.find_features('ProfileFeature')
        return sketches[-1] if sketches else None

    def run_macro(self, macro_path, module_name, sub_name):
        """
        运行 SolidWorks 宏 (兼容 SW2026)

        核心修复: RunMacro2 的 ErrorCode 是 [out] long* 参数
        """
        error_code = win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        try:
            status = self.swApp.RunMacro2(
                macro_path, module_name, sub_name, 0, error_code)
            log.info(f"宏执行状态: {status}, 错误码: {error_code.value}")
            return status
        except Exception as e:
            log.error(f"宏执行失败: {e}")
            return None

    # ================================================================
    #  工具方法
    # ================================================================

    @staticmethod
    def variant_dispatch(value=None):
        """创建 VT_DISPATCH 类型的 VARIANT (用于 Callout 等参数)"""
        return win32com.client.VARIANT(pythoncom.VT_DISPATCH, value)

    @staticmethod
    def variant_byref_int(value=0):
        """创建 VT_BYREF | VT_I4 类型的 VARIANT (用于 [out] long* 参数)"""
        return win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_I4, value)

    @staticmethod
    def variant_byref_variant(value=''):
        """创建 VT_BYREF | VT_VARIANT 类型的 VARIANT"""
        return win32com.client.VARIANT(
            pythoncom.VT_BYREF | pythoncom.VT_VARIANT, value)


# ================================================================
#  快速启动函数
# ================================================================

def connect(use_early_binding=False):
    """快速连接到 SolidWorks"""
    return SWConnection(use_early_binding=use_early_binding)


if __name__ == '__main__':
    # 测试连接
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sw = connect()
    if sw.swModel:
        print(f"活动文档: {sw.swModel.GetPathName}")
    else:
        print("无活动文档，正在创建新零件...")
        sw.new_part()
        print(f"新文档: {sw.swModel.GetPathName}")
