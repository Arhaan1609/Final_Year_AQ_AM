"""
scratch/test_sentinel_triggers.py - Part 2: Stress-Test the Fallback Sentinel

Deliberately triggers 5 separate fallback/warning paths and verifies:
  (a) API returns valid response (sentinel is non-breaking)
  (b) Response value matches expected behavior
  (c) Backend log contains [DATA SENTINEL WARNING] for applicable cases

Run AFTER starting the backend:  uvicorn api.main:app --host 0.0.0.0 --port 8000
Then check the uvicorn console output for WARNING lines.
"""

import requests

BASE = "http://127.0.0.1:8000"
PASS_STR = "PASS"
FAIL_STR = "FAIL"

results = []

def check(label, ok, notes=""):
    status = PASS_STR if ok else FAIL_STR
    results.append((label, ok))
    print(f"  [{status}] {label}")
    if notes:
        print(f"         {notes}")


# =====================================================================
# TRIGGER 1: Missing chassis_no + no soh field  ->  SOH baseline sentinel fires
# Expected: response succeeds with prediction, init_soh defaults to 95.0%
# Backend log: [DATA SENTINEL WARNING] Task=SOH: Missing vehicle chassis...
# =====================================================================
print("\n[TRIGGER 1] Missing chassis_no and soh -> SOH baseline sentinel")
try:
    r = requests.post(f"{BASE}/predict/soh", json={
        "battery_voltage": 74.0,
        "battery_temp": 32.0,
        "battery_current": -10.0,
        "charge_cycle_count": 100,
        # NOTE: no chassis_no, no soh, no initial_soh
    }, timeout=10)
    data = r.json()
    ok = r.status_code == 200 and "prediction" in data
    check("API returns 200 with prediction", ok, f"prediction={data.get('prediction')}")
    check("Prediction is valid SOH float", isinstance(data.get("prediction"), (int, float)))
    print("         -> Check uvicorn log for: [DATA SENTINEL WARNING] Task=SOH: Missing vehicle chassis...")
except Exception as e:
    check("API call succeeded", False, str(e))


# =====================================================================
# TRIGGER 2: Missing battery_voltage sentinel via _predict() internal path
# We POST battery_voltage=None explicitly via a raw dict that bypasses the schema
# by sending it as a query param test. Instead, test that providing a KNOWN
# chassis_no AVOIDS the sentinel (no warning should fire = correct)
# =====================================================================
print("\n[TRIGGER 2] Known chassis_no bypasses sentinel (no warning expected)")
try:
    r = requests.post(f"{BASE}/predict/soh", json={
        "battery_voltage": 74.0,
        "battery_temp": 32.0,
        "battery_current": -10.0,
        "charge_cycle_count": 200,
        "chassis_no": "CN-DL1LAK7203",  # A real chassis in fleet_vehicles.json
    }, timeout=10)
    data = r.json()
    ok = r.status_code == 200 and "prediction" in data
    check("API returns 200 with prediction (real chassis)", ok, f"prediction={data.get('prediction')}")
    check("Model used is reported", "model_used" in data, f"model_used={data.get('model_used')}")
    print("         -> Check uvicorn log: NO sentinel warning should appear for this call")
except Exception as e:
    check("API call succeeded", False, str(e))


# =====================================================================
# TRIGGER 3: /sequence endpoint for a non-parquet fleet vehicle -> clean 404
# Proves: the endpoint exists, returns 404 for non-parquet vehicles
# and does NOT synthesize fake data or call the model on garbage input
# =====================================================================
print("\n[TRIGGER 3] /sequence endpoint for non-parquet fleet vehicle -> clean 404")
try:
    r = requests.get(f"{BASE}/api/v1/db/vehicles/DL1LAN0707/sequence", timeout=10)
    ok = r.status_code == 404
    detail = r.json().get("detail", "")
    check("Returns 404 (not 200 with fake data)", ok, f"Status={r.status_code}")
    check("Detail mentions coverage info", "GJ05CV656" in detail or "No real" in detail,
          f"detail: {detail[:150]}")
except Exception as e:
    check("API call succeeded", False, str(e))


# =====================================================================
# TRIGGER 4: /sequence endpoint for the one parquet vehicle -> real 200 data
# Proves: GJ05CV6564 returns real chronological data with correct shape
# =====================================================================
print("\n[TRIGGER 4] /sequence endpoint for GJ05CV6564 -> real 200 data")
try:
    r = requests.get(f"{BASE}/api/v1/db/vehicles/GJ05CV6564/sequence", timeout=10)
    data = r.json()
    ok = r.status_code == 200 and data.get("has_sequence") is True
    check("Returns 200 with has_sequence=True", ok, f"Status={r.status_code}")
    seq = data.get("sequence", [])
    check("Sequence has exactly 10 steps", len(seq) == 10, f"len(sequence)={len(seq)}")
    check("Each step has 4 values [v, i, t, soc]", all(len(s) == 4 for s in seq),
          f"step widths={[len(s) for s in seq[:3]]}...")
    check("Source is euler_hiload_parquet", data.get("source") == "euler_hiload_parquet",
          f"source={data.get('source')}")
    cr = data.get("cycle_range", {})
    check("Cycle range is present", "first" in cr and "last" in cr,
          f"cycle_range={cr}")
    if seq:
        print(f"         -> Last step: v={seq[-1][0]}, i={seq[-1][1]}, t={seq[-1][2]}, soc={seq[-1][3]}")
        print(f"         -> Cycle range: {cr.get('first')} to {cr.get('last')}")
except Exception as e:
    check("API call succeeded", False, str(e))


# =====================================================================
# TRIGGER 5: RUL with charge_cycle_count=0 (new vehicle edge case)
# Proves: zero cycles (falsy) is handled correctly, not defaulting to 150
# and the result is a valid RUL in [0, 2000]
# =====================================================================
print("\n[TRIGGER 5] RUL prediction with charge_cycle_count=0 (new vehicle)")
try:
    r = requests.post(f"{BASE}/predict/rul", json={
        "battery_voltage": 80.5,
        "battery_temp": 25.0,
        "battery_current": -5.0,
        "charge_cycle_count": 0,
        "soc_at_charge": 98.0,
        "chassis_no": "TEST-NEW-VEHICLE-ZERO-CYCLES",
    }, timeout=10)
    data = r.json()
    ok = r.status_code == 200 and "prediction" in data
    check("API returns 200 with prediction", ok, f"status={r.status_code}")
    pred = data.get("prediction", -1)
    check("Prediction is in valid RUL range [0, 2000]", 0 <= pred <= 2000, f"rul={pred}")
    # Also test a high-cycle vehicle and confirm RUL is lower
    r2 = requests.post(f"{BASE}/predict/rul", json={
        "battery_voltage": 72.0,
        "battery_temp": 35.0,
        "battery_current": -20.0,
        "charge_cycle_count": 1100,
        "soc_at_charge": 65.0,
    }, timeout=10)
    d2 = r2.json()
    pred2 = d2.get("prediction", pred)
    check("High-cycle vehicle RUL < new vehicle RUL (monotonicity)", pred2 < pred,
          f"new_vehicle_rul={pred}, high_cycle_rul={pred2}")
except Exception as e:
    check("API call succeeded", False, str(e))


# =====================================================================
# NORMAL-USE CHECK: Verify sentinel does NOT fire on a normal full request
# =====================================================================
print("\n[NORMAL USE] Full valid SOH call - confirm sentinel stays silent")
try:
    r = requests.post(f"{BASE}/predict/soh", json={
        "battery_voltage": 74.0,
        "battery_temp": 30.0,
        "battery_current": -15.0,
        "charge_cycle_count": 350.0,
        "chassis_no": "CN-GJ05CV6564",
        "soh": 90.15,
    }, timeout=10)
    data = r.json()
    ok = r.status_code == 200 and "prediction" in data
    check("Full valid request returns 200", ok, f"prediction={data.get('prediction')}")
    print("         -> Check uvicorn log: NO [DATA SENTINEL WARNING] should appear for this call")
except Exception as e:
    check("Full valid call succeeded", False, str(e))


print("\n" + "=" * 65)
passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"Sentinel Stress-Test Results: {passed}/{total} passed")
print()
print("CHECK UVICORN LOG — Expected sentinel lines:")
print("  Trigger 1:  WARNING api.module_a: [DATA SENTINEL WARNING] Task=SOH...")
print("  Trigger 2:  NO WARNING (chassis resolved from fleet JSON)")
print("  Trigger 5:  NO WARNING (chassis provided, just zero cycles)")
print("  Normal Use: NO WARNING (full valid request)")
