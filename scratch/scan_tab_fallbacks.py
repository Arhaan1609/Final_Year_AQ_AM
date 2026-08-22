import os
import re

tabs_dir = "frontend/components/tabs"
for f in sorted(os.listdir(tabs_dir)):
    if not f.endswith(".tsx"):
        continue
    path = os.path.join(tabs_dir, f)
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for idx, l in enumerate(lines, 1):
            s = l.strip()
            if s.startswith("//") or s.startswith("/*") or s.startswith("*"):
                continue
            # Look for || <literal> or ?? <literal>
            for op in ["||", "??"]:
                if op in s:
                    parts = s.split(op)
                    if len(parts) > 1:
                        tokens = parts[1].strip().split()
                        if tokens:
                            rhs = tokens[0].rstrip(";,)}")
                            if rhs and (rhs[0].isdigit() or rhs.startswith(('"', "'"))):
                                print(f"{f}:{idx:4d} [{op}] {s[:100]}")
