"""Root test configuration: make the host demo importable.

根测试配置：使宿主演示应用可导入。
"""

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parents[1] / "demos" / "contacts_cli"

if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))
