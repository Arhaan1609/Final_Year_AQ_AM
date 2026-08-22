"""scratch/run_part2.py — Part 2 sentinel verification (ASCII-safe)"""
import requests
BASE = "http://127.0.0.1:8000"
results = []

def chk(label, ok, notes=""):
    results.append((label, ok))
    print(("[PASS] " if ok else "[FAIL] ") + label)
    if notes:
        print("       " + notes)

# 2.1 Missing chassis -> sentinel fires
print("[2.1] Missing chassis -> SOH baseline sentinel fires")
r = requests.post(BASE + "/predict/soh", json={
    "battery_voltage": 74.0, "battery_temp": 32.0,
    "battery_current": -10.0, "charge_cycle_count": 100,
})
d = r.json()
chk("API returns 200 (sentinel non-breaking)", r.status_code == 200)
chk("Prediction present", "prediction" in d, "prediction=" + str(d.get("prediction")))
print("       -> uvicorn shows: [DATA SENTINEL WARNING] Task=SOH: Missing vehicle chassis...")

# 2.2 Known chassis bypasses sentinel
print("[2.2] Known chassis bypasses sentinel")
r = requests.post(BASE + "/predict/soh", json={
    "battery_voltage": 74.0, "battery_temp": 32.0,
    "battery_current": -10.0, "charge_cycle_count": 200,
    "chassis_no": "CN-DL1LAK7203",
})
d = r.json()
chk("Returns 200", r.status_code == 200)
chk("Calibrated XGBoost used", "Calibrated" in d.get("model_used", ""),
    "model_used=" + d.get("model_used", ""))
print("       -> uvicorn: NO sentinel warning")

# 2.3 Sequence 404 for non-parquet vehicle
print("[2.3] Sequence 404 for non-parquet vehicle DL1LAN0707")
r = requests.get(BASE + "/api/v1/db/vehicles/DL1LAN0707/sequence")
detail = r.json().get("detail", "")
chk("Returns clean 404", r.status_code == 404, "status=" + str(r.status_code))
chk("Detail mentions real coverage", "GJ05CV656" in detail,
    "detail=" + detail[:80])

# 2.4 Sequence 200 for real parquet vehicle
print("[2.4] Sequence 200 for GJ05CV6564")
r = requests.get(BASE + "/api/v1/db/vehicles/GJ05CV6564/sequence")
d = r.json()
chk("Returns 200 with has_sequence=True",
    r.status_code == 200 and d.get("has_sequence") is True)
seq = d.get("sequence", [])
chk("10 real steps returned", len(seq) == 10, "n_steps=" + str(len(seq)))
chk("Source is euler_hiload_parquet", d.get("source") == "euler_hiload_parquet")
chk("Cycle range 390-399", d.get("cycle_range", {}).get("first") == 390,
    "cycle_range=" + str(d.get("cycle_range")))

# 2.5 RUL monotonicity
print("[2.5] RUL new vehicle (0 cycles) vs high-wear (1100 cycles)")
r_new = requests.post(BASE + "/predict/rul", json={
    "battery_voltage": 80.5, "battery_temp": 25.0,
    "battery_current": -5.0, "charge_cycle_count": 0,
    "soc_at_charge": 98.0,
})
r_old = requests.post(BASE + "/predict/rul", json={
    "battery_voltage": 72.0, "battery_temp": 35.0,
    "battery_current": -20.0, "charge_cycle_count": 1100,
    "soc_at_charge": 65.0,
})
p_new = r_new.json().get("prediction", -1)
p_old = r_old.json().get("prediction", -1)
chk("New vehicle RUL in [0, 2000]", 0 <= p_new <= 2000, "rul_new=" + str(p_new))
chk("High-cycle RUL < new vehicle RUL", 0 < p_old < p_new,
    "rul_new=" + str(p_new) + ", rul_1100cy=" + str(p_old))

# 2.6 False positive check: full valid call stays silent
print("[2.6] False-positive check: full valid call stays silent")
r = requests.post(BASE + "/predict/soh", json={
    "battery_voltage": 74.0, "battery_temp": 30.0,
    "battery_current": -15.0, "charge_cycle_count": 350.0,
    "chassis_no": "CN-GJ05CV6564", "soh": 90.15,
})
chk("Full valid call returns 200", r.status_code == 200,
    "prediction=" + str(r.json().get("prediction")))
print("       -> uvicorn: NO [DATA SENTINEL WARNING] for this call")

# Summary
passed = sum(1 for _, ok in results if ok)
total = len(results)
print()
print("=" * 55)
print("PART 2 RESULTS: " + str(passed) + "/" + str(total) + " checks passed")
if passed == total:
    print("ALL PASS")
else:
    print("FAILURES: " + str([l for l, ok in results if not ok]))
print("=" * 55)
