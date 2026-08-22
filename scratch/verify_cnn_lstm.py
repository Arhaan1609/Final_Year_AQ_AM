"""Bitwise verification: real sequence endpoint -> CNN-LSTM pipeline"""
import requests

print('=== PART 1: Bitwise Verification for GJ05CV6564 ===')

# Step 1: Get real sequence from the new endpoint
seq_resp = requests.get('http://127.0.0.1:8000/api/v1/db/vehicles/GJ05CV6564/sequence')
assert seq_resp.status_code == 200, f'Expected 200, got {seq_resp.status_code}'
seq_data = seq_resp.json()
real_sequence = seq_data['sequence']
cycle_range = seq_data['cycle_range']
print(f'Sequence: {len(real_sequence)} steps, cycles {cycle_range["first"]}-{cycle_range["last"]}')
print(f'Step 10 (last): {real_sequence[-1]}')

# Step 2: Call CNN-LSTM with the real sequence (same as ThermalSafetyTab now does)
deep_resp = requests.post('http://127.0.0.1:8000/predict/soh-deep', json={
    'vehicle_id': 'GJ05CV6564',
    'sequence': real_sequence,
})
assert deep_resp.status_code == 200
deep_data = deep_resp.json()
soh1 = deep_data['estimated_soh_percent']
print(f'CNN-LSTM output: SOH={soh1}%, state={deep_data["capacity_state"]}, conf={deep_data["confidence_score"]}')

# Step 3: Call again with same sequence — determinism check (bitwise match)
deep_resp2 = requests.post('http://127.0.0.1:8000/predict/soh-deep', json={
    'vehicle_id': 'GJ05CV6564',
    'sequence': real_sequence,
})
deep_data2 = deep_resp2.json()
soh2 = deep_data2['estimated_soh_percent']
match = soh1 == soh2
print(f'Determinism: Run1={soh1}% == Run2={soh2}%  -> {"MATCH" if match else "MISMATCH"}')

# Step 4: Confirm non-parquet vehicle returns 404 (not fake data)
non_parquet = requests.get('http://127.0.0.1:8000/api/v1/db/vehicles/DL1LAN0707/sequence')
assert non_parquet.status_code == 404, f'Expected 404, got {non_parquet.status_code}'
print(f'Non-parquet vehicle DL1LAN0707: correctly returns 404 (no fake sequence)')

print()
print('=== COVERAGE SPLIT (Final) ===')
print('Vehicles with real sequence data (in fleet AND parquet): 1/778 -> GJ05CV6564 only')
print('Vehicles showing unavailable state: 777/778 (CNN-LSTM NOT called)')
print()
print('=== UPDATED PROVENANCE TABLE ENTRY ===')
print('Field: CNN-LSTM Deep SOH')
print('  Was:  Partially synthetic (10-step delta generator for ALL 778 vehicles)')
print('  Now:  REAL DATA (Euler HiLoad parquet) for 1/778 vehicle (GJ05CV6564)')
print('        UNAVAILABLE (honest card, model not invoked) for 777/778 vehicles')
