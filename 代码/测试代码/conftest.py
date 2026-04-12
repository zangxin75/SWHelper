"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "Python脚本"))


@pytest.fixture
def sample_materials():
    """Sample material data for testing"""
    return {
        "铝合金_6061": {"density": 2.7, "yield_strength": 276},
        "不锈钢_304": {"density": 7.93, "yield_strength": 290},
        "碳钢_Q235": {"density": 7.85, "yield_strength": 235}
    }


@pytest.fixture
def sample_user_input():
    """Sample user input for testing"""
    return "创建一个 100x100x50mm 的铝合金方块"
