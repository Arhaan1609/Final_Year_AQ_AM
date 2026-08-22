import json

with open("scratch/raw_fallback_candidates.json") as f:
    candidates = json.load(f)

# Group by component area
by_area = {
    "frontend_tabs": [],
    "frontend_components": [],
    "frontend_lib": [],
    "api_routers": [],
    "modules": []
}

for c in candidates:
    f = c["file"]
    if "frontend/components/tabs" in f:
        by_area["frontend_tabs"].append(c)
    elif "frontend/components" in f:
        by_area["frontend_components"].append(c)
    elif "frontend/lib" in f:
        by_area["frontend_lib"].append(c)
    elif "api" in f:
        by_area["api_routers"].append(c)
    elif "modules" in f:
        by_area["modules"].append(c)

print(f"Tabs: {len(by_area['frontend_tabs'])}")
print(f"Components: {len(by_area['frontend_components'])}")
print(f"Frontend Lib: {len(by_area['frontend_lib'])}")
print(f"API Routers: {len(by_area['api_routers'])}")
print(f"Modules: {len(by_area['modules'])}")

# Detailed printout of frontend tabs & API routers
print("\n" + "="*80)
print("FRONTEND TABS FINDINGS")
print("="*80)
for item in by_area["frontend_tabs"]:
    print(f"[{item['file']}:{item['line']}] ({item['pattern']}) Default: {item['default_value']}")
    print(f"   Snippet: {item['snippet']}")

print("\n" + "="*80)
print("API ROUTERS FINDINGS")
print("="*80)
for item in by_area["api_routers"]:
    print(f"[{item['file']}:{item['line']}] ({item['pattern']}) Default: {item['default_value']}")
    print(f"   Snippet: {item['snippet']}")
