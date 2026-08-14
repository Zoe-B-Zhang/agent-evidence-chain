#!/usr/bin/env python3
"""TrackARuntime 环境自查脚本。

运行方式：
    python scripts/self_check.py

功能：
1. 检查 Python 版本 >= 3.11。
2. 检查 requirements.txt 中的包是否已安装；缺失则自动安装。
3. 给出下一步可执行的验证命令。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_PYTHON = (3, 11)
ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"


def check_python_version() -> bool:
    """检查 Python 版本是否满足最低要求。"""
    ok = sys.version_info >= REQUIRED_PYTHON
    print(f"Python version: {sys.version}")
    if not ok:
        print(
            f"[FAIL] Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required, "
            f"found {sys.version_info.major}.{sys.version_info.minor}",
            file=sys.stderr,
        )
    else:
        print("[PASS] Python version OK")
    return ok


def parse_requirements(path: Path) -> list[str]:
    """解析 requirements.txt，返回包名列表（忽略注释和空行）。"""
    packages: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        # 取包名（忽略版本说明符，仅用于 import 检查）
        pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("<")[0].split(">")[0].strip()
        packages.append(pkg)
    return packages


def import_name(package: str) -> str:
    """将 pip 包名映射到 import 名。"""
    mapping = {"pyyaml": "yaml"}
    return mapping.get(package.lower(), package.lower())


def check_and_install_packages() -> bool:
    """检查并自动安装缺失包。"""
    if not REQUIREMENTS.exists():
        print(f"[FAIL] {REQUIREMENTS} not found", file=sys.stderr)
        return False

    packages = parse_requirements(REQUIREMENTS)
    missing: list[str] = []
    for pkg in packages:
        module = import_name(pkg)
        try:
            __import__(module)
            print(f"[PASS] {pkg} imported as '{module}'")
        except ImportError:
            print(f"[WARN] {pkg} not installed; will install")
            missing.append(pkg)

    if not missing:
        return True

    print(f"\nInstalling missing packages: {missing}")
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"[FAIL] pip install failed: {exc}", file=sys.stderr)
        return False

    # 再次检查
    for pkg in missing:
        module = import_name(pkg)
        try:
            __import__(module)
            print(f"[PASS] {pkg} installed and importable")
        except ImportError:
            print(f"[FAIL] {pkg} still not importable after install", file=sys.stderr)
            return False
    return True


def print_next_steps() -> None:
    print("\n=== Next steps ===")
    print("  python cli.py run --task \"fix failing test\"")
    print("  python cli.py eval")
    print("  python cli.py harness --prompt v1 --gray-percent 0")
    print("  python -m unittest discover tests")


def main() -> int:
    ok = check_python_version() and check_and_install_packages()
    print_next_steps()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
