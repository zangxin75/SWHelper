# Simple pytest configuration for sw2026 project
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "代码" / "Python脚本"))
