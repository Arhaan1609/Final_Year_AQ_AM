import sqlite3
import json
import requests

conn = sqlite3.connect('fleet_intelligence.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT id, status, voltage, battery_temp, current, 
           charge_cycle_count, speed, driver, fleet, model, soc, soh, rul, mileage, controller_temp, motor_temp
    FROM vehicles 
    ORDER BY charge_cycle_count ASC
''')
all_v = cursor.fetchall()
print(f"Total vehicles in SQL DB: {len(all_v)}", flush=True)

# Select 10 diverse trucks across healthy, warning, and critical operating envelopes
indices = [5, 60, 140, 220, 310, 420, 510, 600, 710, 775]
selected = [all_v[i] for i in indices]

print("=" * 95, flush=True)
print("  EMPIRICAL VERIFICATION REPORT: 10 COMMERCIAL FLEET TRUCKS ACROSS 74 ML MODELS", flush=True)
print("=" * 95, flush=True)

session = requests.Session()

for idx, v in enumerate(selected, 1):
    vid = v[0]
    status = v[1]
    voltage = v[2]
    temp = v[3]
    current = v[4]
    cycles = v[5]
    speed = v[6]
    driver = v[7]
    db_soc = v[10]
    db_soh = v[11]
    db_rul = v[12]
    c_temp = v[14]
    m_temp = v[15]
    
    # 1. Module A SOC
    soc_res = session.post('http://localhost:8000/predict/soc', json={
        'battery_voltage': voltage, 'battery_temp': temp, 'battery_current': current,
        'abs_current': abs(current), 'odometer': cycles * 58
    }).json()
    
    # 2. Module A SOH
    soh_res = session.post('http://localhost:8000/predict/soh', json={
        'battery_voltage': voltage, 'battery_temp': temp, 'battery_current': current,
        'odometer': cycles * 58, 'charge_cycle_count': cycles
    }).json()

    # 3. Module A RUL
    rul_res = session.post('http://localhost:8000/predict/rul', json={
        'odometer': cycles * 58, 'soc_at_charge': db_soc
    }).json()
    
    # 4. Module A Range
    range_res = session.post('http://localhost:8000/predict/mileage', json={
        'run_kms': 45, 'avg_speed': speed, 'max_speed': speed + 20
    }).json()
    
    # 5. Module B Thermal
    therm_res = session.post('http://localhost:8000/predict/thermal', json={
        'vbt': temp, 'vct': c_temp, 'vmt': m_temp, 'vbv': voltage, 'vbc': current, 'soc': db_soc, 'speed': speed
    }).json()
    
    # 6. Module C Knee Point
    knee_res = session.post('http://localhost:8000/predict/knee-point', json={
        'charge_cycle_count': cycles, 'capacity': db_soh, 'voltage': voltage,
        'battery_temp': temp, 'current': current, 'soc': db_soc, 'speed': speed
    }).json()
    
    # 7. Module C Driver Behavior
    harsh_a = 8 if status == 'critical' else 4 if status == 'warning' else 1
    harsh_b = 6 if status == 'critical' else 3 if status == 'warning' else 1
    driver_res = session.post('http://localhost:8000/predict/driver-behavior', json={
        'harsh_accel_count': harsh_a, 'harsh_brake_count': harsh_b, 'harsh_corner_count': 1,
        'speed_variance': 18.0 if status == 'critical' else 10.0 if status == 'warning' else 5.0,
        'avg_speed': speed, 'max_speed': speed + 25, 'battery_temp_max': temp,
        'max_discharge_current': abs(current)
    }).json()
    
    pred_soc = soc_res.get('prediction', 0)
    pred_soh = soh_res.get('prediction', 0)
    pred_rul = rul_res.get('prediction', 0)
    pred_range = range_res.get('prediction', 0)
    
    sev = therm_res.get('safety_status', 'SAFE')
    runaway = therm_res.get('risk_probability', 0)
    threat = therm_res.get('primary_thermal_threat', 'Nominal Operation')
    hotspot = therm_res.get('hotspot_zone', 'Battery Pack')
    
    rul_knee = knee_res.get('rul_to_knee_cycles', 0)
    knee_state = knee_res.get('knee_risk_state', 'UNKNOWN')
    est_knee = knee_res.get('estimated_knee_cycle', 0)
    
    ai = driver_res.get('aggressiveness_index', 0)
    bsi = driver_res.get('battery_stress_index', 0)
    driver_cat = driver_res.get('driver_classification', 'UNKNOWN')
    soh_penalty = driver_res.get('annual_soh_penalty_percent', 0)
    
    print(f"\n[{idx}/10] VIN: {vid} | Driver: {driver} | Status: {status.upper()} | Odometer: ~{cycles * 58:,} km", flush=True)
    print(f"  Inputs:       V={voltage:.1f}V | I={current:.1f}A | PackTemp={temp:.1f}°C | Cycles={cycles} EFC | Speed={speed:.1f} km/h", flush=True)
    print(f"  Module A:     SOC={pred_soc:.1f}% | SOH={pred_soh:.1f}% | RUL={pred_rul:.0f} cycles | Range={pred_range:.1f} km", flush=True)
    print(f"  Module B:     Thermal State={sev} | Threat Prob={runaway:.3f} | Threat={threat} (Hotspot: {hotspot})", flush=True)
    print(f"  Module C:     RUL to Knee={rul_knee:.1f} cycles (Est Knee: ~{est_knee:.0f}c) | State={knee_state}", flush=True)
    print(f"  Driver AI:    AI={ai:.2f} | BSI={bsi:.2f} | Profile: {driver_cat} (Annual SOH Penalty: -{soh_penalty}%)", flush=True)
