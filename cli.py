"""
cli.py — Root-level shortcut to launch the interactive prediction CLI.

Equivalent to: python modules/module_a/07_prediction_system.py
"""
import os
import sys
import subprocess

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_CLI_SCRIPT   = os.path.join(_PROJECT_ROOT, "modules", "module_a", "07_prediction_system.py")
_MODULE_A_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_a")

if __name__ == "__main__":
    subprocess.run([sys.executable, _CLI_SCRIPT], cwd=_MODULE_A_DIR)
