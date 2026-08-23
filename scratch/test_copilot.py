import sys, os
sys.path.insert(0, os.path.abspath("."))
from api.services.copilot_service import explain_vehicle_performance, chat_copilot


telemetry = {
    'chassis': 'CN-DL1LAP5083',
    'fleet': 'Delhi NCR Fleet Hub',
    'status': 'critical',
    'battery_temp': 30.0,
    'voltage': 74.5,
    'current': -20.0,
    'speed': 42.0,
    'charge_cycle_count': 776
}
predictions = {'soc': 55.9, 'soh': 70.5, 'rul': 941, 'mileage': 98.4}

res = explain_vehicle_performance('DL1LAP5083', telemetry, predictions, force_refresh=True)
print("=== EXPLAIN VEHICLE RESULT ===")
print("Model Used:", res.get("model_used"))
print("Urgency:", res.get("urgency"))
print("Summary:", res.get("summary"))
print("Why:", res.get("why_performing_this_way"))
print("Root Causes:", res.get("root_causes"))
print("Actions:", res.get("prescriptive_actions"))

chat_res = chat_copilot("Why is this vehicle on hold?", [], active_vehicle=telemetry, active_predictions=predictions)
print("\n=== CHAT COPILOT RESULT ===")
print("Model Used:", chat_res.get("model_used"))
print("Reply:", chat_res.get("reply")[:300])
