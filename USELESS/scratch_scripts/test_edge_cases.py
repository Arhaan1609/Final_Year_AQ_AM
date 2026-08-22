import requests

session = requests.Session()

edge_cases = [
    {'name': '1. Fresh Pack (0 cycles, 25°C, 76.5V)', 'data': {'v': 76.5, 'i': -10.0, 't': 25.0, 'cycles': 0, 'soc': 100.0, 'speed': 20.0}},
    {'name': '2. Mid Life (500 cycles, 35°C, 74.0V)', 'data': {'v': 74.0, 'i': -25.0, 't': 35.0, 'cycles': 500, 'soc': 60.0, 'speed': 35.0}},
    {'name': '3. High Wear (950 cycles, 42°C, 71.5V)', 'data': {'v': 71.5, 'i': -45.0, 't': 42.0, 'cycles': 950, 'soc': 30.0, 'speed': 45.0}},
    {'name': '4. Extreme Stress (1200 cycles, 55°C, 68.0V)', 'data': {'v': 68.0, 'i': -65.0, 't': 55.0, 'cycles': 1200, 'soc': 15.0, 'speed': 55.0}},
    {'name': '5. Regenerative Braking (+30A current, 78.5V)', 'data': {'v': 78.5, 'i': 30.0, 't': 33.0, 'cycles': 200, 'soc': 80.0, 'speed': 25.0}},
]

print("=" * 80)
print("  EDGE CASE & BOUNDARY INTEGRITY TEST")
print("=" * 80)

for ec in edge_cases:
    name = ec['name']
    d = ec['data']
    soc_res = session.post('http://localhost:8000/predict/soc', json={'battery_voltage': d['v'], 'battery_temp': d['t'], 'battery_current': d['i'], 'abs_current': abs(d['i']), 'odometer': d['cycles'] * 58}).json()
    soh_res = session.post('http://localhost:8000/predict/soh', json={'battery_voltage': d['v'], 'battery_temp': d['t'], 'battery_current': d['i'], 'odometer': d['cycles'] * 58, 'charge_cycle_count': d['cycles']}).json()
    rul_res = session.post('http://localhost:8000/predict/rul', json={'odometer': d['cycles'] * 58, 'soc_at_charge': d['soc']}).json()
    knee_res = session.post('http://localhost:8000/predict/knee-point', json={'charge_cycle_count': d['cycles'], 'capacity': soh_res.get('prediction', 90.0), 'voltage': d['v'], 'battery_temp': d['t'], 'current': d['i'], 'soc': d['soc'], 'speed': d['speed']}).json()
    therm_res = session.post('http://localhost:8000/predict/thermal', json={'vbt': d['t'], 'vct': d['t'] + 10, 'vmt': d['t'] + 20, 'vbv': d['v'], 'vbc': d['i'], 'soc': d['soc'], 'speed': d['speed']}).json()
    
    pred_soc = soc_res.get('prediction')
    pred_soh = soh_res.get('prediction')
    pred_rul = rul_res.get('prediction')
    pred_knee = knee_res.get('rul_to_knee_cycles')
    knee_state = knee_res.get('knee_risk_state')
    therm_state = therm_res.get('safety_status')
    therm_risk = therm_res.get('risk_probability')
    
    print(f"\n* {name}")
    print(f"   SOC: {pred_soc}% | SOH: {pred_soh}% | RUL: {pred_rul} cycles")
    print(f"   Knee: RUL to Knee = {pred_knee} cycles ({knee_state})")
    print(f"   Thermal: {therm_state} (Risk Probability: {therm_risk:.3f})")
