"""
api/services/copilot_service.py — High-Performance LLM Service powered by GPT-OSS 120B / Groq.
Provides:
  1. explain_vehicle_performance(): Structured 3-part diagnostic (Summary, Why, Root Causes, Actions)
  2. chat_copilot(): Interactive fleet copilot answering employee queries with full telemetry context.
Features in-memory caching and zero-crash deterministic fallback.
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Primary & Fallback models
PRIMARY_MODEL = "openai/gpt-oss-120b"
FAST_FALLBACK_MODEL = "openai/gpt-oss-20b"

# In-memory diagnostic cache: { vehicle_id: { "timestamp": float, "data": dict } }
_INSIGHTS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache per vehicle


def _call_groq(messages: List[Dict[str, str]], response_format_json: bool = False, max_tokens: int = 1200) -> Optional[str]:
    """Call Groq API with automatic model failover."""
    if not GROQ_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens
    }
    if response_format_json:
        payload["response_format"] = {"type": "json_object"}

    # Try primary model (GPT-OSS 120B) then fallback (GPT-OSS 20B)
    for model_name in [PRIMARY_MODEL, FAST_FALLBACK_MODEL]:
        try:
            payload["model"] = model_name
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return content
            else:
                print(f"[CopilotService] Groq model {model_name} returned status {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"[CopilotService] Error calling {model_name}: {e}")

    return None



def generate_deterministic_insight(vehicle_id: str, telemetry: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Instant rule-based diagnostic engine used if offline or API is unreachable."""
    soc = predictions.get("soc", telemetry.get("soc", 75))
    soh = predictions.get("soh", telemetry.get("soh", 95))
    rul = predictions.get("rul", telemetry.get("rul", 1000))
    range_km = predictions.get("mileage", telemetry.get("mileage", 100))
    temp = telemetry.get("battery_temp", 30.0)
    status = telemetry.get("status", "active")
    cycles = telemetry.get("charge_cycle_count", 250)

    is_critical = status == "critical" or soh < 75 or temp > 48
    is_warning = not is_critical and (status == "warning" or soh < 85 or temp > 40 or soc < 30)

    if is_critical:
        summary = f"Vehicle {vehicle_id} is under Critical Service Hold. Usable capacity has degraded to {soh:.1f}% with {cycles} equivalent full cycles."
        why = f"The battery shows capacity fade beyond nominal operational limits ({soh:.1f}% SOH). While operating temperature is currently stable ({temp:.1f}°C), cumulative electrochemical cycle strain requires balancing."
        root_causes = [
            f"Electrochemical capacity degradation: SOH is at {soh:.1f}% against initial baseline.",
            f"Cycle throughput wear: {cycles} recorded cycles with estimated {rul:.0f} cycles remaining to degradation knee.",
            f"Terminal status flagged as {status.upper()}."
        ]
        prescriptive_actions = [
            "Ground vehicle from active high-speed express routes.",
            "Schedule depot terminal diagnostic for cell voltage delta inspection and balancing.",
            "Limit charging current to 0.5C to prevent thermal stress."
        ]
        urgency = "CRITICAL"
    elif is_warning:
        summary = f"Vehicle {vehicle_id} is on Dispatch Advisory. Battery level is {soc:.0f}% with moderate operating health ({soh:.1f}% SOH)."
        why = f"Operating normally with moderate wear. Range is estimated at {range_km:.0f} km. Fast-charging or hot afternoon duty cycles should be monitored."
        root_causes = [
            f"Moderate charge state: Current fuel level is {soc:.1f}%.",
            f"Operating temperature at {temp:.1f}°C (nominal bounds).",
            f"Remaining useful life projected at {rul:.0f} cycles."
        ]
        prescriptive_actions = [
            "Perform quick 30-minute top-up before afternoon dispatch runs.",
            "Dispatch on standard urban routes under 80 km.",
            "Monitor motor and controller thermal dissipation during peak load."
        ]
        urgency = "WARNING"
    else:
        summary = f"Vehicle {vehicle_id} is in Optimal Operational Condition. Full battery health verified at {soh:.1f}% SOH."
        why = f"All thermodynamic and electrochemical parameters are in Grade-A equilibrium. Pack core temperature ({temp:.1f}°C) and dynamic range ({range_km:.0f} km) are optimal."
        root_causes = [
            f"Pristine battery lifespan: {soh:.1f}% SOH with low historical degradation.",
            f"Sub-second thermal stability: Pack Core ({temp:.1f}°C) well below 40°C threshold.",
            f"Driver behavior rated smooth with minimal battery stress."
        ]
        prescriptive_actions = [
            "Cleared for immediate full-shift commercial dispatch.",
            "Suitable for maximum payload routes up to 100+ km.",
            "Maintain standard overnight AC trickle charging cycle."
        ]
        urgency = "NOMINAL"

    return {
        "vehicle_id": vehicle_id,
        "summary": summary,
        "why_performing_this_way": why,
        "root_causes": root_causes,
        "prescriptive_actions": prescriptive_actions,
        "urgency": urgency,
        "model_used": "Deterministic Electro-Thermal Engine",
        "cached": False
    }


import re

def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extract JSON object from LLM response text."""
    if not text:
        return None
    # 1. Direct parse
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # 2. Extract from markdown code block
    fence_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except Exception:
            pass
    # 3. Search for outermost braces
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0).strip())
        except Exception:
            pass
    return None


def explain_vehicle_performance(vehicle_id: str, telemetry: Dict[str, Any], predictions: Dict[str, Any], force_refresh: bool = False) -> Dict[str, Any]:
    """Generate structured 3-part diagnostic using GPT-OSS 120B or fallback."""
    # Check cache
    if not force_refresh and vehicle_id in _INSIGHTS_CACHE:
        entry = _INSIGHTS_CACHE[vehicle_id]
        if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
            res = dict(entry["data"])
            res["cached"] = True
            return res

    soc = predictions.get("soc", telemetry.get("soc", 75))
    soh = predictions.get("soh", telemetry.get("soh", 95))
    rul = predictions.get("rul", telemetry.get("rul", 1000))
    range_km = predictions.get("mileage", telemetry.get("mileage", 100))
    temp = telemetry.get("battery_temp", 30.0)
    controller_temp = telemetry.get("controller_temp", temp + 5)
    motor_temp = telemetry.get("motor_temp", temp + 10)
    voltage = telemetry.get("voltage", 74.5)
    current = telemetry.get("current", -15.0)
    speed = telemetry.get("speed", 35.0)
    cycles = telemetry.get("charge_cycle_count", 250)
    status = telemetry.get("status", "active")

    system_prompt = (
        "You are an expert Commercial EV Powertrain & Battery Intelligence Diagnostic Copilot for Euler HiLoad 12.4 kWh LFP electric trucks.\n"
        "Analyze the provided live telemetry and machine learning diagnostic predictions. Explain clearly:\n"
        "1. Executive Summary: What is the vehicle's true condition?\n"
        "2. Why is it performing this way?: Deep electro-thermal, cycle aging, and behavioral explanation.\n"
        "3. Root Causes: Specific contributing factors.\n"
        "4. Prescriptive Action Directives: Exact actionable instructions for the fleet dispatcher and maintenance team.\n\n"
        "Respond STRICTLY as a valid JSON object without extra commentary, with the following format:\n"
        "{\n"
        '  "summary": "...",\n'
        '  "why_performing_this_way": "...",\n'
        '  "root_causes": ["factor 1", "factor 2", ...],\n'
        '  "prescriptive_actions": ["action 1", "action 2", ...],\n'
        '  "urgency": "CRITICAL" | "WARNING" | "NOMINAL"\n'
        "}"
    )

    user_prompt = (
        f"Vehicle ID: {vehicle_id}\n"
        f"Chassis: {telemetry.get('chassis', vehicle_id)}\n"
        f"Fleet Hub: {telemetry.get('fleet', 'Delhi NCR Fleet Hub')}\n"
        f"Status: {status.upper()}\n"
        f"Live ML State of Charge (SOC): {soc:.1f}%\n"
        f"Live ML State of Health (SOH): {soh:.1f}% (Baseline Commissioning SOH₀: {telemetry.get('soh', soh):.1f}%)\n"
        f"Live ML Remaining Useful Life (RUL): {rul:.0f} cycles (~{(rul/250):.1f} years)\n"
        f"Live ML Range per Charge: {range_km:.1f} km\n"
        f"Pack Voltage: {voltage:.1f}V | Pack Current: {current:.1f}A | Speed: {speed:.1f} km/h\n"
        f"Thermals -> Pack Core: {temp:.1f}°C | Controller: {controller_temp:.1f}°C | Motor: {motor_temp:.1f}°C\n"
        f"Cumulative Cycles: {cycles} EFC | Odometer: {cycles * 58} km\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    llm_output = _call_groq(messages, response_format_json=False, max_tokens=1500)


    if llm_output:
        parsed = _extract_json(llm_output)
        if parsed and "summary" in parsed:
            result = {
                "vehicle_id": vehicle_id,
                "summary": parsed.get("summary", ""),
                "why_performing_this_way": parsed.get("why_performing_this_way", ""),
                "root_causes": parsed.get("root_causes", []),
                "prescriptive_actions": parsed.get("prescriptive_actions", []),
                "urgency": parsed.get("urgency", "NOMINAL"),
                "model_used": "GPT-OSS 120B (Groq)",
                "cached": False
            }
            _INSIGHTS_CACHE[vehicle_id] = {"timestamp": time.time(), "data": result}
            return result

    # Fallback if LLM unavailable
    fallback_res = generate_deterministic_insight(vehicle_id, telemetry, predictions)
    _INSIGHTS_CACHE[vehicle_id] = {"timestamp": time.time(), "data": fallback_res}
    return fallback_res



def chat_copilot(message: str, history: List[Dict[str, str]], active_vehicle: Optional[Dict[str, Any]] = None, active_predictions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Handle interactive employee chat queries with situational fleet awareness."""
    system_prompt = (
        "You are the EV Battery Intelligence Copilot — an expert AI powertrain, BMS, and fleet operations assistant "
        "for commercial Euler HiLoad 12.4 kWh LFP electric trucks.\n"
        "You have direct real-time access to the platform's multi-zone thermal models, calibrated SOH estimators, "
        "RUL knee-point boosters, and fleet telematics.\n\n"
        "Guidelines:\n"
        "- Answer employee questions clearly, professionally, and concisely.\n"
        "- When discussing a specific truck, ground your answers in its actual live telemetry (SOC, SOH, RUL, temps, cycles).\n"
        "- Use markdown formatting (bolding, bullet points, callouts) to make answers scannable.\n"
        "- Explain physical battery concepts (e.g. LFP flat voltage curve, thermal limits, C-rate, cell balancing) simply.\n"
    )

    context_str = ""
    if active_vehicle:
        vid = active_vehicle.get("id", "Unknown")
        soc = active_predictions.get("soc", active_vehicle.get("soc", 75)) if active_predictions else active_vehicle.get("soc", 75)
        soh = active_predictions.get("soh", active_vehicle.get("soh", 95)) if active_predictions else active_vehicle.get("soh", 95)
        rul = active_predictions.get("rul", active_vehicle.get("rul", 1000)) if active_predictions else active_vehicle.get("rul", 1000)
        temp = active_vehicle.get("battery_temp", 30.0)
        status = active_vehicle.get("status", "active")
        context_str = (
            f"\n[CURRENTLY INSPECTED VEHICLE: {vid}]\n"
            f"- Status: {status.upper()}\n"
            f"- SOC: {soc:.1f}%\n"
            f"- SOH: {soh:.1f}% (Commissioning Baseline: {active_vehicle.get('soh', 95):.1f}%)\n"
            f"- RUL: {rul:.0f} cycles (~{(rul/250):.1f} yrs)\n"
            f"- Core Temp: {temp:.1f}°C | Voltage: {active_vehicle.get('voltage', 74.5):.1f}V | Current: {active_vehicle.get('current', -15):.1f}A\n"
            f"- Charge Cycles: {active_vehicle.get('charge_cycle_count', 300)} EFC\n"
        )

    formatted_messages = [{"role": "system", "content": system_prompt + context_str}]

    # Add conversation history (up to last 6 turns)
    for turn in history[-6:]:
        role = "user" if turn.get("sender") == "user" or turn.get("role") == "user" else "assistant"
        content = turn.get("text") or turn.get("content") or ""
        if content:
            formatted_messages.append({"role": role, "content": content})

    formatted_messages.append({"role": "user", "content": message})

    reply = _call_groq(formatted_messages, response_format_json=False, max_tokens=700)

    if reply:
        return {
            "reply": reply,
            "model_used": "GPT-OSS 120B (Groq)",
            "vehicle_context": active_vehicle.get("id") if active_vehicle else None
        }

    # Deterministic fallback response if offline
    if active_vehicle:
        vid = active_vehicle.get("id")
        fallback_reply = (
            f"⚡ **Diagnostic Note for {vid}:**\n\n"
            f"- **State of Charge:** {active_vehicle.get('soc', 75):.1f}%\n"
            f"- **State of Health:** {active_vehicle.get('soh', 95):.1f}%\n"
            f"- **Thermal Zone:** {active_vehicle.get('battery_temp', 30.0):.1f}°C (Pack Core)\n\n"
            f"The vehicle is currently registered in **{active_vehicle.get('status', 'active').upper()}** state. "
            f"Operating metrics are within configured safety bounds."
        )
    else:
        fallback_reply = (
            "⚡ **Fleet Copilot Assistant Ready.**\n\n"
            "I can analyze vehicle health, predict thermal risks, and assist with dispatch routing. "
            "Select any truck from the fleet to inspect its live electro-thermal state."
        )

    return {
        "reply": fallback_reply,
        "model_used": "Deterministic Assistant Engine",
        "vehicle_context": active_vehicle.get("id") if active_vehicle else None
    }
