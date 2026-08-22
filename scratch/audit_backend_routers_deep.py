import os
import re

api_files = [
    "api/routers/module_a.py",
    "api/routers/module_b.py",
    "api/routers/module_c.py",
    "api/routers/fleet.py",
    "api/routers/copilot.py",
    "api/main.py",
    "api/schemas.py",
    "api/db/database.py"
]

all_api_findings = []

for fpath in api_files:
    if not os.path.exists(fpath): continue
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            l = line.strip()
            if l.startswith("#"): continue
            
            # Check 1: dict.get(key, default) with numeric or string default
            m_get = re.search(r'\.get\(\s*["\']([a-zA-Z0-9_-]+)["\']\s*,\s*([^)]+)\)', l)
            if m_get:
                val = m_get.group(2).strip()
                if val not in ["None", "null", "{}", "[]", "''", "\"\""]:
                    all_api_findings.append({
                        "file": fpath,
                        "line": idx,
                        "code": l,
                        "key": m_get.group(1),
                        "default": val,
                        "type": "DICT_GET_FALLBACK"
                    })
            
            # Check 2: getattr(obj, attr, default)
            m_attr = re.search(r'getattr\([^,]+,\s*["\']([a-zA-Z0-9_-]+)["\']\s*,\s*([^)]+)\)', l)
            if m_attr:
                val = m_attr.group(2).strip()
                if val not in ["None", "null"]:
                    all_api_findings.append({
                        "file": fpath,
                        "line": idx,
                        "code": l,
                        "key": m_attr.group(1),
                        "default": val,
                        "type": "GETATTR_FALLBACK"
                    })

print(f"Total API Findings: {len(all_api_findings)}")
for f in all_api_findings:
    print(f"[{f['file']}:{f['line']:3d}] ({f['type']}) key '{f['key']}' -> default: {f['default']}")
    print(f"   Code: {f['code'][:100]}")
