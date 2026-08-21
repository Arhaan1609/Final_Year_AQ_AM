import os
import sys

# Add modules/module_b to sys.path so tests can import `src`
_MODULE_B_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _MODULE_B_DIR)
