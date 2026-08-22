import os
import re
import json

TARGET_DIRS = ["frontend/components", "frontend/lib", "api", "modules"]
EXCLUDE_DIRS = ["node_modules", ".next", "__pycache__", "USELESS", ".git"]

patterns = [
    (r"\.get\(\s*['\"][a-zA-Z0-9_-]+['\"]\s*,\s*([^)]+)\)", "dict.get(key, default)"),
    (r"\?\?\s*([0-9\.]+|['\"][^'\"]+['\"])", "Nullish coalescing default (?? literal)"),
    (r"\|\|\s*([0-9\.]+|['\"][^'\"]+['\"])", "Logical OR default (|| literal)"),
    (r"getattr\([^,]+,[^,]+,\s*([^)]+)\)", "getattr default"),
    (r"(fallback|mock|dummy|placeholder|stub|nominal|assumed)", "Keyword match (fallback/mock/dummy/stub/nominal/assumed)"),
    (r"try:.*?(?:except|catch).*?(return\s+[^;\n]+)", "try/except returning default"),
]

findings = []

for base in TARGET_DIRS:
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if not f.endswith((".py", ".ts", ".tsx", ".js")):
                continue
            fpath = os.path.join(root, f)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
                    lines = file.readlines()
                    for idx, line in enumerate(lines, 1):
                        stripped = line.strip()
                        # Ignore comments
                        if stripped.startswith(("//", "#", "/*", "*")):
                            continue
                        
                        # 1. Regex checks
                        for pat, desc in patterns:
                            matches = re.finditer(pat, stripped, re.IGNORECASE)
                            for m in matches:
                                val = m.group(1) if m.groups() else m.group(0)
                                # Filter out noise (e.g. get('key') with no default or boolean / null)
                                if desc == "dict.get(key, default)" and val.strip() in ["None", "null", "{}", "[]", "''", "\"\""]:
                                    continue
                                findings.append({
                                    "file": fpath.replace("\\", "/"),
                                    "line": idx,
                                    "snippet": stripped[:120],
                                    "pattern": desc,
                                    "default_value": val.strip()[:40]
                                })
            except Exception as e:
                print(f"Error reading {fpath}: {e}")

print(f"Total raw candidates found: {len(findings)}")
with open("scratch/raw_fallback_candidates.json", "w") as out:
    json.dump(findings, out, indent=2)

print("Saved raw candidates to scratch/raw_fallback_candidates.json")
