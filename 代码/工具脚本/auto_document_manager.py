#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude Code 文档自动管理工具
自动分类、命名和归档Claude生成的文档
"""
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DocumentAutoManager:
    """文档自动管理器"""

    def __init__(self, project_root: str = "D:\\sw2026"):
        """初始化文档管理器"""
        self.project_root = Path(project_root)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        # 默认配置
        config = {
            "research_reports": {
                "keywords": ["调研", "研究", "分析", "报告", "可行性"],
                "directory": "文档/研究报告/",
                "naming_pattern": "{主题}_研究报告.md"
            },
            "user_guides": {
                "keywords": ["指南", "教程", "快速开始", "使用", "入门"],
                "directory": "文档/使用指南/",
                "naming_pattern": "{功能}_快速启动指南.md"
            },
            "technical_docs": {
                "keywords": ["API", "架构", "设计", "接口", "规范", "技术"],
                "directory": "文档/技术文档/",
                "naming_pattern": "{组件}_技术文档.md"
            },
            "project_management": {
                "keywords": ["计划", "进度", "报告", "总结", "项目"],
                "directory": "文档/项目管理/",
                "naming_pattern": "{类型}_{项目名称}_{日期}.md"
            },
            "knowledge_base": {
                "keywords": ["最佳实践", "经验", "技巧", "优化", "问题"],
                "directory": "文档/知识库/",
                "naming_pattern": "{主题}_知识条目.md"
            },
            # 代码文件
            "python_scripts": {
                "extensions": [".py"],
                "directory": "代码/Python脚本/",
                "naming_pattern": "{功能}.py"
            },
            "vba_macros": {
                "extensions": [".bas", ".swb"],
                "directory": "代码/VBA宏/",
                "naming_pattern": "{零件}_{操作}.bas"
            }
        }

        # 尝试加载外部配置
        config_file = self.project_root / ".claude" / "rules.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    external_config = json.load(f)
                    # 提取classification_rules
                    if "document_management" in external_config:
                        if "classification_rules" in external_config["document_management"]:
                            config.update(external_config["document_management"]["classification_rules"])
            except Exception as e:
                print(f"Warning: Failed to load external config: {e}")

        return config

    def classify_document(self, title: str, content: str = "", file_ext: str = ".md") -> Dict:
        """
        自动分类文档

        Args:
            title: 文档标题
            content: 文档内容（可选）
            file_ext: 文件扩展名（可选）

        Returns:
            分类信息字典
        """
        # 分析文档类型
        doc_type = self._identify_document_type(title, content, file_ext)

        # 确定目录
        directory = self._get_directory_for_type(doc_type)

        # 生成文件名
        filename = self._generate_filename(title, doc_type, file_ext)

        return {
            "type": doc_type,
            "directory": directory,
            "filename": filename,
            "full_path": str(self.project_root / directory / filename)
        }

    def _identify_document_type(self, title: str, content: str, file_ext: str) -> str:
        """识别文档类型"""
        # 先检查文件扩展名
        if file_ext == ".py":
            return "python_scripts"
        elif file_ext in [".bas", ".swb"]:
            return "vba_macros"
        elif file_ext == ".json":
            return "config"

        # 基于标题和内容关键词分析
        title_lower = title.lower()

        # 优先级顺序匹配
        for doc_type, type_config in self.config.items():
            # 配置结构：type_config包含"keywords"键
            if "keywords" in type_config:
                for keyword in type_config["keywords"]:
                    if keyword in title or keyword in title_lower:
                        return doc_type

        # 基于内容分析
        if content:
            content_lower = content.lower()

            # 检查内容关键词
            if any(word in content_lower for word in ["研究", "调研", "分析", "可行性"]):
                return "research_reports"
            elif any(word in content_lower for word in ["指南", "教程", "快速开始", "使用方法"]):
                return "user_guides"
            elif any(word in content_lower for word in ["api", "架构", "接口", "技术文档"]):
                return "technical_docs"
            elif any(word in content_lower for word in ["计划", "进度", "项目总结"]):
                return "project_management"

        # 默认为知识库
        return "knowledge_base"

    def _get_directory_for_type(self, doc_type: str) -> str:
        """获取文档类型对应的目录"""
        return self.config.get(doc_type, {}).get("directory", "文档/其他/")

    def _generate_filename(self, title: str, doc_type: str, file_ext: str) -> str:
        """生成文件名"""
        # 清理标题
        clean_title = self._clean_title(title)

        # 获取命名模式
        pattern = self.config.get(doc_type, {}).get("naming_pattern", "{标题}{扩展名}")

        # 获取日期
        today = datetime.now().strftime("%Y-%m-%d")

        # 生成文件名
        filename = pattern
        filename = filename.replace("{主题}", clean_title)
        filename = filename.replace("{功能}", clean_title)
        filename = filename.replace("{组件}", clean_title)
        filename = filename.replace("{类型}", clean_title.split('_')[0] if '_' in clean_title else clean_title)
        filename = filename.replace("{项目名称}", "SolidWorks_Agent")
        filename = filename.replace("{日期}", today)
        filename = filename.replace("{标题}", clean_title)
        filename = filename.replace("{扩展名}", file_ext)

        # 确保有扩展名
        if not filename.endswith(file_ext):
            filename += file_ext

        return filename

    def _clean_title(self, title: str) -> str:
        """清理标题，生成合法的文件名"""
        # 移除不允许的字符
        illegal_chars = r'[\/:*?"<>|]'
        clean_title = re.sub(illegal_chars, '', title)

        # 移除多余空格和特殊符号
        clean_title = re.sub(r'\s+', '_', clean_title.strip())
        clean_title = re.sub(r'_{2,}', '_', clean_title)

        # 移除开头和结尾的下划线
        clean_title = clean_title.strip('_')

        # 限制长度
        if len(clean_title) > 50:
            clean_title = clean_title[:50]

        return clean_title

    def save_document(self, title: str, content: str,
                      file_ext: str = ".md",
                      force_overwrite: bool = False) -> Dict:
        """
        保存文档到自动分类的位置

        Args:
            title: 文档标题
            content: 文档内容
            file_ext: 文件扩展名
            force_overwrite: 是否覆盖已存在的文件

        Returns:
            保存结果
        """
        # 分类文档
        classification = self.classify_document(title, content, file_ext)

        # 创建目录（如果不存在）
        directory_path = self.project_root / classification["directory"]
        directory_path.mkdir(parents=True, exist_ok=True)

        # 完整文件路径
        file_path = self.project_root / classification["directory"] / classification["filename"]

        # 检查文件是否已存在
        if file_path.exists() and not force_overwrite:
            # 添加版本标识
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_part = classification["filename"].rsplit('.', 1)[0]
            ext_part = classification["filename"].rsplit('.', 1)[1]
            new_filename = f"{name_part}_v{timestamp}.{ext_part}"
            file_path = self.project_root / classification["directory"] / new_filename

        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file_path": str(file_path),
                "relative_path": f"{classification['directory']}{classification['filename']}",
                "classification": classification,
                "message": f"✅ 文档已保存到: {classification['directory']}{classification['filename']}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ 保存失败: {e}"
            }

    def organize_existing_files(self, source_dir: str = ".") -> Dict:
        """
        整理现有文件

        Args:
            source_dir: 源目录（默认为项目根目录）

        Returns:
            整理结果
        """
        source_path = self.project_root / source_dir
        results = {
            "moved": [],
            "skipped": [],
            "errors": []
        }

        # 需要排除的目录
        exclude_dirs = {
            '.git', '.venv', 'node_modules', '__pycache__',
            '文档', '代码', '项目', '配置', '模型文件', '.claude', '.omc'
        }

        # 遍历源目录中的文件
        for file_path in source_path.rglob("*"):
            # 跳过目录和已排除的目录
            if file_path.is_dir() or any(exclude in file_path.parts for exclude in exclude_dirs):
                continue

            # 只处理特定文件类型
            if file_path.suffix not in ['.md', '.py', '.bas', '.swb']:
                continue

            # 跳过隐藏文件
            if file_path.name.startswith('.'):
                continue

            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取标题
                title = file_path.stem
                if file_path.suffix == '.md':
                    # 从Markdown文件提取标题
                    for line in content.split('\n')[:10]:
                        if line.strip().startswith('# '):
                            title = line.strip()[2:]
                            break

                # 分类并移动
                classification = self.classify_document(title, content, file_path.suffix)
                target_dir = self.project_root / classification["directory"]
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / classification["filename"]

                # 避免覆盖已存在的文件
                if target_path.exists():
                    results["skipped"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "reason": "目标文件已存在"
                    })
                else:
                    # 移动文件
                    shutil.move(str(file_path), str(target_path))
                    results["moved"].append({
                        "from": str(file_path.relative_to(self.project_root)),
                        "to": str(target_path.relative_to(self.project_root))
                    })
                    print(f"  📁 {file_path.name} -> {classification['directory']}{classification['filename']}")

            except Exception as e:
                results["errors"].append({
                    "file": str(file_path.relative_to(self.project_root)),
                    "error": str(e)
                })
                print(f"  ❌ {file_path.name}: {e}")

        return results

    def analyze_directory(self, directory: str = ".") -> Dict:
        """
        分析目录中的文件

        Args:
            directory: 要分析的目录

        Returns:
            分析结果
        """
        dir_path = self.project_root / directory

        analysis = {
            "total_files": 0,
            "by_type": {},
            "unclassified": [],
            "suggestions": []
        }

        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue

            analysis["total_files"] += 1

            # 分析文件类型
            if file_path.suffix == '.md':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    title = file_path.stem
                    for line in content.split('\n')[:5]:
                        if line.strip().startswith('# '):
                            title = line.strip()[2:]
                            break

                    classification = self.classify_document(title, content, file_path.suffix)
                    doc_type = classification["type"]

                    if doc_type not in analysis["by_type"]:
                        analysis["by_type"][doc_type] = []
                    analysis["by_type"][doc_type].append(str(file_path))

                except Exception:
                    analysis["unclassified"].append(str(file_path))

        return analysis


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行接口"""
    import sys

    # 设置UTF-8编码
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    manager = DocumentAutoManager()

    if len(sys.argv) < 2:
        print("="*60)
        print("🤖 Claude Code 文档自动管理工具")
        print("="*60)
        print("\n用法:")
        print("  python auto_document_manager.py save <标题> <内容>")
        print("  python auto_document_manager.py classify <标题>")
        print("  python auto_document_manager.py organize [源目录]")
        print("  python auto_document_manager.py analyze [目录]")
        print("\n示例:")
        print("  python auto_document_manager.py save \"新功能设计\" \"# 内容...\"")
        print("  python auto_document_manager.py organize")
        return

    command = sys.argv[1]

    if command == "classify":
        # 分类文档
        title = sys.argv[2] if len(sys.argv) > 2 else "示例文档"

        classification = manager.classify_document(title)

        print("\n📋 文档分类结果:")
        print(f"  标题: {title}")
        print(f"  类型: {classification['type']}")
        print(f"  目录: {classification['directory']}")
        print(f"  文件名: {classification['filename']}")
        print(f"  完整路径: {classification['full_path']}")

    elif command == "save":
        # 保存文档
        title = sys.argv[2]

        if len(sys.argv) > 3:
            # 从文件读取内容
            with open(sys.argv[3], 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            # 使用默认内容
            content = f"# {title}\n\n文档内容..."

        result = manager.save_document(title, content)

        if result["success"]:
            print(result["message"])
        else:
            print(f"❌ {result['message']}")

    elif command == "organize":
        # 整理现有文件
        source_dir = sys.argv[2] if len(sys.argv) > 2 else "."

        print("\n🔄 开始整理文件...")
        print(f"源目录: {source_dir}")
        print("-"*60)

        results = manager.organize_existing_files(source_dir)

        print("\n📊 整理结果:")
        print(f"  ✅ 移动: {len(results['moved'])} 个文件")
        print(f"  ⏭️  跳过: {len(results['skipped'])} 个文件")
        print(f"  ❌ 错误: {len(results['errors'])} 个文件")

        if results["moved"]:
            print(f"\n移动的文件:")
            for item in results["moved"]:
                print(f"  {item['from']}")
                print(f"    → {item['to']}")

    elif command == "analyze":
        # 分析目录
        target_dir = sys.argv[2] if len(sys.argv) > 2 else "."

        analysis = manager.analyze_directory(target_dir)

        print(f"\n📊 目录分析: {target_dir}")
        print("-"*60)
        print(f"总文件数: {analysis['total_files']}")

        if analysis["by_type"]:
            print(f"\n按类型分类:")
            for doc_type, files in analysis["by_type"].items():
                print(f"  {doc_type}: {len(files)} 个")

    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
