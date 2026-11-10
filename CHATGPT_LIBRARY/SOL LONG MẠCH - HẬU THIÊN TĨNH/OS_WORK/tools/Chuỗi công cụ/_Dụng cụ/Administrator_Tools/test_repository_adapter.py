"""Load Administrator Tools tests from the colocated tool with its own source-bound fixtures."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[0]
SOURCE=ROOT/'CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/Chuỗi công cụ/_Dụng cụ/Administrator_Tools/tests/test_administrator_tools.py'
spec=importlib.util.spec_from_file_location('administrator_tools_canonical_suite',SOURCE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
AdministratorToolsTests=mod.AdministratorToolsTests