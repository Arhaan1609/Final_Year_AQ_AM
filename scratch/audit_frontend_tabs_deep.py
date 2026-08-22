import os
import re

tabs = [
    "FleetOverviewTab.tsx",
    "StateEstimationTab.tsx",
    "ThermalSafetyTab.tsx",
    "DriverProfilingTab.tsx",
    "KneePrognosticsTab.tsx",
    "MetaEnsembleReportTab.tsx",
    "DigitalTwin3DTab.tsx"
]

all_tab_findings = []

for t in tabs:
    p = os.path.join("frontend/components/tabs", t)
    if not os.path.exists(p):
        continue
    with open(p, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            l = line.strip()
            if l.startswith("//") or l.startswith("/*") or l.startswith("*"):
                continue
            
            # Check 1: Logical OR with numeric fallback: || <num>
            m_or = re.search(r'([a-zA-Z0-9_.?()]+)\s*\|\|\s*([0-9\.]+)', l)
            if m_or:
                all_tab_findings.append({
                    "tab": t,
                    "line": idx,
                    "code": l,
                    "target": m_or.group(1),
                    "default": m_or.group(2),
                    "type": "OR_NUMERIC_FALLBACK",
                    "risk": "Falsy zero bug: 0 values will silently convert to " + m_or.group(2)
                })

            # Check 2: Nullish coalescing with numeric fallback: ?? <num>
            m_nullish = re.search(r'([a-zA-Z0-9_.?()]+)\s*\?\?\s*([0-9\.]+)', l)
            if m_nullish:
                all_tab_findings.append({
                    "tab": t,
                    "line": idx,
                    "code": l,
                    "target": m_nullish.group(1),
                    "default": m_nullish.group(2),
                    "type": "NULLISH_NUMERIC_FALLBACK",
                    "risk": "Substitutes default " + m_nullish.group(2) + " if null/undefined"
                })

            # Check 3: String fallback: || "STRING"
            m_str = re.search(r'([a-zA-Z0-9_.?()]+)\s*\|\|\s*(["\'][^"\']+["\'])', l)
            if m_str:
                all_tab_findings.append({
                    "tab": t,
                    "line": idx,
                    "code": l,
                    "target": m_str.group(1),
                    "default": m_str.group(2),
                    "type": "OR_STRING_FALLBACK",
                    "risk": "Substitutes string " + m_str.group(2) + " if null/falsy"
                })

print(f"Total Tab Findings: {len(all_tab_findings)}")
for f in all_tab_findings:
    print(f"[{f['tab']}:{f['line']:3d}] ({f['type']}) {f['target']} -> default: {f['default']}")
    print(f"   Code: {f['code'][:100]}")
