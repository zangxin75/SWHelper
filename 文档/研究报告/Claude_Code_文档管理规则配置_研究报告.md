# Claude Code 文档管理规则配置

**版本**: 1.0
**创建日期**: 2026-04-12
**项目路径**: `D:\sw2026`

---

## 🎯 核心目标

实现Claude Code生成的文档**自动分类、自动命名、自动归档**，使用中文目录和文件名，便于管理和查找。

---

## 📂 文档分类体系

### 一级分类（按用途）

```
D:\sw2026\
├── 📄 文档\                          # 所有项目文档
│   ├── 研究报告\                     # 技术调研、市场分析、方案对比
│   ├── 使用指南\                     # 用户手册、教程、快速参考
│   ├── 技术文档\                     # API文档、架构设计、接口说明
│   ├── 项目管理\                     # 计划、进度、报告、总结
│   └── 知识库\                       # 最佳实践、经验总结、问题解决
│
├── 💻 代码\                          # 源代码文件
│   ├── Python脚本\                   # Python自动化脚本
│   ├── VBA宏\                        # SolidWorks宏文件
│   ├── 测试代码\                     # 测试和验证代码
│   └── 工具脚本\                     # 辅助工具和脚本
│
├── 🎯 项目\                          # 独立子项目
│   ├── SolidworksMCP-python\          # Python MCP服务器
│   ├── SolidworksMCP-TS\              # TypeScript MCP服务器
│   └── python-automation\             # Python自动化工具
│
├── 📦 模型文件\                       # SolidWorks文件
│   ├── 零件\                         # 3D零件(.SLDPRT)
│   ├── 装配体\                       # 装配体(.SLDASM)
│   ├── 工程图\                       # 工程图(.SLDDRW)
│   └── 宏文件\                       # 宏文件(.SWB)
│
└── 🗂️ 配置\                          # 配置文件
    ├── agent_config.json             # Agent配置
    ├── mcp_config.json               # MCP配置
    └── environment.env               # 环境变量
```

### 二级分类（按类型）

#### 研究报告细分
```
文档/研究报告/
├── 技术调研\                         # 技术方案调研
├── 市场分析\                         # 市场和竞品分析
├── 方案对比\                         # 不同方案的对比分析
└── 可行性分析\                       # 技术可行性分析
```

#### 使用指南细分
```
文档/使用指南/
├── 快速开始\                         # 新手入门指南
├── 功能教程\                         # 详细功能教程
├── 最佳实践\                         # 使用最佳实践
├── 常见问题\                         # FAQ和故障排除
└── 视频教程\                         # 视频和演示
```

#### 技术文档细分
```
文档/技术文档/
├── API文档\                          # API接口文档
├── 架构设计\                         # 系统架构文档
├── 数据模型\                         # 数据结构说明
├── 接口规范\                         # 接口定义和规范
└── 部署运维\                         # 部署和运维文档
```

---

## 📝 文档命名规范

### 命名格式

```
{主标题}_{副标题}_{版本/日期}.{扩展名}
```

### 各类文档命名规则

#### 研究报告
```
格式: {主题}_研究报告.md
示例: 
- SolidWorks_2026_AI_Agent_自动化研究报告.md
- Claude_Code_API集成研究报告.md
- 性能基准测试研究报告.md
```

#### 使用指南
```
格式: {功能}_快速启动指南.md 或 {功能}_使用手册.md
示例:
- AI_Agent_快速启动指南.md
- MCP服务器_部署手册.md
- Agent开发_教程.md
```

#### 技术文档
```
格式: {组件}_API文档.md 或 {组件}_技术文档.md
示例:
- Agent_Coordinator_API文档.md
- COM适配器_技术文档.md
- MCP协议_接口规范.md
```

#### 项目管理
```
格式: {类型}_{项目名称}_{日期}.md
示例:
- 项目计划_SolidWorks_Agent_2026-04-12.md
- 进度报告_第一阶段_2026-04-12.md
- 项目总结_AI_Agent_2026-04-12.md
```

### 命名规则

1. **使用中文**: 文件名使用中文，便于识别
2. **下划线分隔**: 使用 `_` 而不是 `-` 分隔词汇
3. **避免特殊字符**: 不使用 `/ \ : * ? " < > |`
4. **版本标识**: 重要文档包含版本号或日期
5. **简洁明确**: 文件名要清楚表达文档内容

---

## 🤖 Claude Code 文档生成规则

### 规则1: 自动分类识别

Claude Code在生成文档前，先识别文档类型：

```python
# 文档类型识别规则
DOCUMENT_TYPES = {
    # 研究报告类
    "研究报告": ["调研", "研究", "分析", "对比", "可行性"],
    
    # 使用指南类
    "使用指南": ["教程", "指南", "快速开始", "入门", "使用"],
    
    # 技术文档类
    "技术文档": ["API", "架构", "设计", "接口", "规范", "数据模型"],
    
    # 项目管理类
    "项目管理": ["计划", "进度", "报告", "总结", "会议", "里程碑"],
    
    # 知识库类
    "知识库": ["最佳实践", "经验", "问题解决", "优化", "技巧"]
}
```

### 规则2: 自动路径生成

根据文档类型，自动生成保存路径：

```python
# 路径生成规则
PATH_RULES = {
    "研究报告": "文档/研究报告/",
    "使用指南": "文档/使用指南/",
    "技术文档": "文档/技术文档/",
    "项目管理": "文档/项目管理/",
    "知识库": "文档/知识库/",
    
    # 代码文件
    "Python脚本": "代码/Python脚本/",
    "VBA宏": "代码/VBA宏/",
    "测试代码": "代码/测试代码/",
    
    # 配置文件
    "配置": "配置/"
}
```

### 规则3: 自动文件命名

根据文档内容，自动生成中文文件名：

```python
# 文件命名规则
NAMING_RULES = {
    "研究报告": lambda title: f"{title}_研究报告.md",
    "使用指南": lambda title: f"{title}_快速启动指南.md" if "快速" in title else f"{title}_使用手册.md",
    "技术文档": lambda title: f"{title}_技术文档.md",
    "项目管理": lambda title, date: f"{title}_{date}.md"
}
```

---

## 🔧 自动化实现

### 方式1: Claude Code Hook配置

创建 `.claude/rules.json`:

```json
{
  "document_management": {
    "enabled": true,
    "auto_classify": true,
    "use_chinese": true,
    "naming_convention": "chinese_underscore",
    
    "classification_rules": {
      "research_reports": {
        "keywords": ["调研", "研究", "分析", "报告"],
        "directory": "文档/研究报告/",
        "naming_pattern": "{主题}_研究报告.md"
      },
      
      "user_guides": {
        "keywords": ["指南", "教程", "快速开始", "使用"],
        "directory": "文档/使用指南/",
        "naming_pattern": "{功能}_快速启动指南.md"
      },
      
      "technical_docs": {
        "keywords": ["API", "架构", "设计", "技术文档"],
        "directory": "文档/技术文档/",
        "naming_pattern": "{组件}_技术文档.md"
      },
      
      "project_management": {
        "keywords": ["计划", "进度", "报告", "总结"],
        "directory": "文档/项目管理/",
        "naming_pattern": "{类型}_{项目名称}_{日期}.md"
      }
    },
    
    "code_files": {
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
  }
}
```

### 方式2: Python自动化脚本

创建 `代码/工具脚本/auto_document_manager.py`:

```python
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
        config_file = self.project_root / ".claude" / "rules.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "research_reports": {
                "keywords": ["调研", "研究", "分析", "报告", "可行性"],
                "directory": "文档/研究报告/",
                "naming_pattern": "{主题}_研究报告.md"
            },
            "user_guides": {
                "keywords": ["指南", "教程", "快速开始", "使用"],
                "directory": "文档/使用指南/",
                "naming_pattern": "{功能}_快速启动指南.md"
            },
            "technical_docs": {
                "keywords": ["API", "架构", "设计", "接口", "规范"],
                "directory": "文档/技术文档/",
                "naming_pattern": "{组件}_技术文档.md"
            },
            "project_management": {
                "keywords": ["计划", "进度", "报告", "总结"],
                "directory": "文档/项目管理/",
                "naming_pattern": "{类型}_{项目名称}_{日期}.md"
            }
        }
    
    def classify_document(self, title: str, content: str = "") -> Dict:
        """
        自动分类文档
        
        Args:
            title: 文档标题
            content: 文档内容（可选）
            
        Returns:
            分类信息字典
        """
        # 分析文档类型
        doc_type = self._identify_document_type(title, content)
        
        # 确定目录
        directory = self._get_directory_for_type(doc_type)
        
        # 生成文件名
        filename = self._generate_filename(title, doc_type)
        
        return {
            "type": doc_type,
            "directory": directory,
            "filename": filename,
            "full_path": str(self.project_root / directory / filename)
        }
    
    def _identify_document_type(self, title: str, content: str) -> str:
        """识别文档类型"""
        # 基于标题关键词
        for doc_type, config in self.config.items():
            for keyword in config["keywords"]:
                if keyword in title:
                    return doc_type
        
        # 基于内容分析
        if content:
            if "# " in content and "## " in content:
                # Markdown文档，进一步分析
                if "研究" in content or "调研" in content or "分析" in content:
                    return "research_reports"
                elif "指南" in content or "教程" in content or "使用" in content:
                    return "user_guides"
                elif "API" in content or "架构" in content or "设计" in content:
                    return "technical_docs"
        
        # 默认为项目管理
        return "project_management"
    
    def _get_directory_for_type(self, doc_type: str) -> str:
        """获取文档类型对应的目录"""
        return self.config.get(doc_type, {}).get("directory", "文档/其他/")
    
    def _generate_filename(self, title: str, doc_type: str) -> str:
        """生成文件名"""
        # 清理标题
        clean_title = self._clean_title(title)
        
        # 获取命名模式
        pattern = self.config.get(doc_type, {}).get("naming_pattern", "{标题}.md")
        
        # 生成文件名
        if "{主题}" in pattern:
            filename = pattern.replace("{主题}", clean_title)
        elif "{功能}" in pattern:
            filename = pattern.replace("{功能}", clean_title)
        elif "{组件}" in pattern:
            filename = pattern.replace("{组件}", clean_title)
        elif "{类型}" in pattern and "{项目名称}" in pattern and "{日期}" in pattern:
            # 项目管理类文档
            today = datetime.now().strftime("%Y-%m-%d")
            filename = pattern.replace("{类型}", clean_title)\
                              .replace("{项目名称}", "SolidWorks_Agent")\
                              .replace("{日期}", today)
        else:
            filename = f"{clean_title}.md"
        
        return filename
    
    def _clean_title(self, title: str) -> str:
        """清理标题，生成合法的文件名"""
        # 移除不允许的字符
        illegal_chars = r'[\/:*?"<>|]'
        clean_title = re.sub(illegal_chars, '', title)
        
        # 移除多余空格
        clean_title = re.sub(r'\s+', '_', clean_title.strip())
        
        # 限制长度
        if len(clean_title) > 50:
            clean_title = clean_title[:50]
        
        return clean_title
    
    def save_document(self, title: str, content: str, 
                      force_overwrite: bool = False) -> Dict:
        """
        保存文档到自动分类的位置
        
        Args:
            title: 文档标题
            content: 文档内容
            force_overwrite: 是否覆盖已存在的文件
            
        Returns:
            保存结果
        """
        # 分类文档
        classification = self.classify_document(title, content)
        
        # 创建目录（如果不存在）
        directory_path = self.project_root / classification["directory"]
        directory_path.mkdir(parents=True, exist_ok=True)
        
        # 完整文件路径
        file_path = self.project_root / classification["directory"] / classification["filename"]
        
        # 检查文件是否已存在
        if file_path.exists() and not force_overwrite:
            # 添加时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_part = classification["filename"].rsplit('.', 1)[0]
            ext_part = classification["filename"].rsplit('.', 1)[1]
            new_filename = f"{name_part}_{timestamp}.{ext_part}"
            file_path = self.project_root / classification["directory"] / new_filename
        
        # 保存文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "classification": classification,
                "message": f"文档已保存到: {file_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"保存失败: {e}"
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
        
        # 遍历源目录中的.md和.py文件
        for file_path in source_path.glob("*.md"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取标题（第一行#后面的内容）
                    title = file_path.stem
                    for line in content.split('\n')[:10]:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                    
                    # 分类并移动
                    classification = self.classify_document(title, content)
                    target_dir = self.project_root / classification["directory"]
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_path = target_dir / classification["filename"]
                    
                    # 移动文件
                    if not target_path.exists():
                        shutil.move(str(file_path), str(target_path))
                        results["moved"].append({
                            "from": str(file_path),
                            "to": str(target_path)
                        })
                    else:
                        results["skipped"].append({
                            "file": str(file_path),
                            "reason": "目标文件已存在"
                        })
                
                except Exception as e:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": str(e)
                    })
        
        return results


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """命令行接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python auto_document_manager.py classify <标题> <内容文件>")
        print("  python auto_document_manager.py save <标题> <内容文件>")
        print("  python auto_document_manager.py organize [源目录]")
        return
    
    manager = DocumentAutoManager()
    command = sys.argv[1]
    
    if command == "classify":
        # 分类文档
        title = sys.argv[2] if len(sys.argv) > 2 else "示例文档"
        content = ""
        
        if len(sys.argv) > 3:
            with open(sys.argv[3], 'r', encoding='utf-8') as f:
                content = f.read()
        
        classification = manager.classify_document(title, content)
        print("文档分类结果:")
        print(f"  类型: {classification['type']}")
        print(f"  目录: {classification['directory']}")
        print(f"  文件名: {classification['filename']}")
        print(f"  完整路径: {classification['full_path']}")
    
    elif command == "organize":
        # 整理现有文件
        source_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        results = manager.organize_existing_files(source_dir)
        
        print("文件整理结果:")
        print(f"  移动: {len(results['moved'])} 个文件")
        print(f"  跳过: {len(results['skipped'])} 个文件")
        print(f"  错误: {len(results['errors'])} 个文件")
        
        if results["moved"]:
            print("\n移动的文件:")
            for item in results["moved"]:
                print(f"  {item['from']} -> {item['to']}")
    
    elif command == "save":
        # 保存文档
        title = sys.argv[2]
        content_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if content_file:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = "# " + title + "\n\n文档内容..."
        
        result = manager.save_document(title, content)
        
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()
```

### 方式3: Claude Code Hook脚本

创建 `.claude/hooks/pre-write.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude Code Pre-Write Hook
在Claude写入文件前自动分类和命名
"""
import sys
import os
from pathlib import Path

# 添加工具脚本路径
sys.path.insert(0, str(Path(__file__).parent.parent / "代码" / "工具脚本"))

from auto_document_manager import DocumentAutoManager

def should_intercept(file_path: str, content: str) -> bool:
    """判断是否需要拦截处理"""
    # 只处理.md和.py文件
    if not (file_path.endswith('.md') or file_path.endswith('.py')):
        return False
    
    # 不处理已分类目录中的文件
    if any(x in file_path for x in ['文档/', '代码/', '配置/', '项目/']):
        return False
    
    # 不处理隐藏文件
    if os.path.basename(file_path).startswith('.'):
        return False
    
    return True

def pre_write_hook(file_path: str, content: str) -> dict:
    """
    写入前Hook函数
    
    Args:
        file_path: 原始文件路径
        content: 文件内容
        
    Returns:
        处理结果，包含新的文件路径
    """
    if not should_intercept(file_path, content):
        return {"intercepted": False, "original_path": file_path}
    
    # 提取标题
    title = os.path.splitext(os.path.basename(file_path))[0]
    
    # 第一行如果是#开头，使用作为标题
    for line in content.split('\n')[:5]:
        if line.strip().startswith('# '):
            title = line.strip()[2:]
            break
    
    # 使用文档管理器分类
    manager = DocumentAutoManager()
    
    # 保存到正确位置
    result = manager.save_document(title, content, force_overwrite=False)
    
    if result["success"]:
        print(f"🤖 自动分类: {file_path} -> {result['file_path']}")
        return {
            "intercepted": True,
            "new_path": result["file_path"],
            "original_path": file_path
        }
    else:
        return {
            "intercepted": False,
            "original_path": file_path,
            "error": result.get("error")
        }

# Claude Code Hook入口点
if __name__ == "claude_hook":
    # 从stdin读取参数
    import json
    data = json.loads(sys.stdin.read())
    
    result = pre_write_hook(data.get("file_path", ""), data.get("content", ""))
    
    # 输出结果
    print(json.dumps(result))
```

---

## 📋 使用指南

### Claude Code内置规则

在生成文档时，Claude Code会自动：

1. **识别文档类型**
   - 分析标题和内容关键词
   - 确定文档所属分类

2. **确定保存路径**
   - 根据分类选择对应目录
   - 自动创建不存在的目录

3. **生成中文文件名**
   - 提取文档标题
   - 应用命名规范
   - 添加必要的后缀

4. **保存到正确位置**
   - 保存到对应分类目录
   - 避免文件名冲突

### 示例1: 生成研究报告

**用户输入**:
```
Claude, 请帮我生成一份关于Claude Code与SolidWorks集成的技术研究报告
```

**Claude Code自动处理**:
1. 识别类型: 研究报告
2. 选择目录: `文档/研究报告/`
3. 生成文件名: `Claude_Code_SolidWorks集成_研究报告.md`
4. 保存位置: `D:\sw2026\文档\研究报告\Claude_Code_SolidWorks集成_研究报告.md`

### 示例2: 生成使用指南

**用户输入**:
```
Claude, 创建一个Agent开发的快速入门教程
```

**Claude Code自动处理**:
1. 识别类型: 使用指南
2. 选择目录: `文档/使用指南/`
3. 生成文件名: `Agent开发_快速启动指南.md`
4. 保存位置: `D:\sw2026\文档\使用指南\Agent开发_快速启动指南.md`

---

## 🔧 配置使用

### 1. 创建Hook配置

创建 `.claude/HOOKS.json`:

```json
{
  "pre-write": {
    "enabled": true,
    "script": ".claude/hooks/pre-write.py",
    "intercept_patterns": [
      "*.md",
      "*.py"
    ],
    "exclude_patterns": [
      "文档/*",
      "代码/*",
      "项目/*",
      ".*"
    ]
  },
  
  "document_management": {
    "auto_classify": true,
    "use_chinese": true,
    "create_backup": false,
    "naming_convention": "chinese_underscore"
  }
}
```

### 2. 测试自动分类

```bash
cd D:\sw2026

# 测试分类功能
python 代码/工具脚本/auto_document_manager.py classify "测试文档"

# 测试保存功能
python 代码/工具脚本/auto_document_manager.py save "新的Agent设计方案" content.txt

# 整理现有文件
python 代码/工具脚本/auto_document_manager.py organize
```

---

## 📊 文档模板

### 研究报告模板

**文件**: `配置/模板/研究报告模板.md`

```markdown
# {主题}研究报告

**报告日期**: {YYYY-MM-DD}
**研究主题**: {简短描述}
**作者**: Claude Code AI Assistant

---

## 执行摘要
{1-2段总结核心发现和建议}

## 研究背景
{背景介绍和问题定义}

## 主要发现
{研究发现和数据分析}

## 技术方案
{技术实施建议}

## 结论与建议
{结论和下一步行动}

## 参考资料
{链接和引用}

---

**报告生成**: Claude Code AI Agent
**最后更新**: {YYYY-MM-DD}
```

### 使用指南模板

**文件**: `配置/模板/使用指南模板.md`

```markdown
# {功能}快速启动指南

**版本**: 1.0
**更新日期**: {YYYY-MM-DD}
**适用对象**: {目标用户}

---

## 🚀 快速开始
{5分钟内可完成的步骤}

## 📋 详细说明
{详细的操作步骤}

## 💡 使用示例
{实际使用案例}

## ❓ 常见问题
{FAQ和故障排除}

## 🔗 相关资源
{相关链接和文档}

---

**维护者**: {维护者信息}
**最后更新**: {YYYY-MM-DD}
```

### 技术文档模板

**文件**: `配置/模板/技术文档模板.md`

```markdown
# {组件}技术文档

**版本**: {版本号}
**最后更新**: {YYYY-MM-DD}

---

## 概述
{组件简介和用途}

## API参考
{接口说明和方法}

## 数据模型
{数据结构定义}

## 配置选项
{配置参数说明}

## 示例代码
{代码示例}

## 故障排除
{常见问题和解决方案}

---

**技术支持**: {支持信息}
**文档版本**: {版本号}
```

---

## 🎯 最佳实践

### 1. 文档标题规范

**✅ 好的标题**:
```
Claude_Code_SolidWorks_集成_研究报告.md
Agent开发_快速启动指南.md
MCP服务器_API文档.md
```

**❌ 不好的标题**:
```
doc.md
test.py
新建文档.md
```

### 2. 内容组织

- ✅ 使用清晰的标题层级
- ✅ 提供目录和导航
- ✅ 包含代码示例
- ✅ 添加图表说明
- ✅ 提供相关链接

### 3. 版本控制

- ✅ 在文档底部记录修改历史
- ✅ 重大修改时更新版本号
- ✅ 保留重要的历史版本

---

## 🔍 文档查找

### 按类型查找

```bash
# 查找所有研究报告
find 文档/研究报告/ -name "*.md"

# 查找所有使用指南
find 文档/使用指南/ -name "*指南.md"

# 查找所有技术文档
find 文档/技术文档/ -name "*文档.md"
```

### 按关键词查找

```bash
# 查找包含"Agent"的文档
find 文档/ -name "*Agent*.md"

# 查找最近7天的文档
find 文档/ -name "*.md" -mtime -7
```

---

## 📞 维护和支持

### 定期维护

- **每周**: 检查新增文档是否正确分类
- **每月**: 更新文档索引，清理过时内容
- **每季度**: 审查分类体系的合理性

### 文档审核

- **准确性**: 确保内容正确无误
- **完整性**: 检查是否有遗漏章节
- **时效性**: 更新过时的信息

---

**配置版本**: 1.0
**创建日期**: 2026-04-12
**维护者**: Claude Code AI Assistant

---

<div align="center">

### 🎯 Claude Code文档管理规则配置完成！

### 现在生成的文档将自动分类到对应的中文目录中！

</div>
