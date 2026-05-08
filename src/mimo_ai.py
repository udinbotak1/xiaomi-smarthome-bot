"""
🤖 Xiaomi MIMO AI Integration
Process natural language commands for smart home control.
"""

import json
import os
import httpx

MIMO_API_URL = "https://api.xiaomimimo.com/v1/chat/completions"


def get_mimo_response(user_message: str, device_context: str = "") -> dict:
    """
    Use Xiaomi MIMO to parse natural language into smart home commands.
    Returns structured action data.
    """
    api_key = os.environ.get("MIMO_API_KEY", "")
    model = os.environ.get("MIMO_MODEL", "mimo-v2-pro")

    system_prompt = f"""You are a smart home AI assistant. Parse the user's natural language command into a structured action.

Available devices:
{device_context}

Respond in JSON format:
{{
    "action": "control|scene|query|schedule",
    "device_id": "device_id or null",
    "command": "on|off|set|get|scene_name",
    "params": {{"brightness": 50, "temperature": 24, ...}},
    "response": "Human-friendly response in Indonesian"
}}

Examples:
- "turn on living room light" → {{"action":"control","device_id":"lr_light_1","command":"on","params":{{}},"response":"✅ Lampu ruang tamu dinyalakan!"}}
- "set AC to 22 degrees" → {{"action":"control","device_id":"lr_ac","command":"set","params":{{"temperature":22}},"response":"✅ AC diatur ke 22°C!"}}
- "good night" → {{"action":"scene","device_id":null,"command":"sleep","params":{{}},"response":"😴 Mode malam diaktifkan!"}}
- "how much power" → {{"action":"query","device_id":null,"command":"power","params":{{}},"response":"⚡ Checking power consumption..."}}
"""

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }
        resp = httpx.post(MIMO_API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Try to parse JSON from response
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        return json.loads(content)

    except Exception as e:
        # Fallback to simple keyword matching
        return parse_command_fallback(user_message)


def parse_command_fallback(text: str) -> dict:
    """Simple keyword-based command parser when MIMO API is unavailable."""
    text = text.lower().strip()

    # Scene triggers
    scenes = {
        "good night": "sleep", "tidur": "sleep", "sleep": "sleep",
        "movie": "movie", "nonton": "movie", "film": "movie",
        "away": "away", "pergi": "away", "pulang": "away",
        "party": "party", "pesta": "party",
        "good morning": "morning", "pagi": "morning", "morning": "morning",
    }
    for trigger, scene in scenes.items():
        if trigger in text:
            return {
                "action": "scene",
                "device_id": None,
                "command": scene,
                "params": {},
                "response": f"🎬 Scene '{scene}' diaktifkan!",
            }

    # Power query
    if any(w in text for w in ["power", "energy", "listrik", "watt", "konsumsi"]):
        return {
            "action": "query",
            "device_id": None,
            "command": "power",
            "params": {},
            "response": "⚡ Cek konsumsi daya...",
        }

    # Simple ON/OFF
    is_on = any(w in text for w in ["on", "nyala", "hidupkan", "turn on"])
    is_off = any(w in text for w in ["off", "mati", "matikan", "turn off"])

    device_map = {
        "light": "light", "lamp": "light", "lampu": "light", "cahaya": "light",
        "ac": "ac", "air conditioner": "ac", "pendingin": "ac",
        "fan": "fan", "kipas": "fan",
        "lock": "lock", "kunci": "lock", "pintu": "lock", "door": "lock",
    }

    room_map = {
        "living": "Living Room", "ruang tamu": "Living Room",
        "bedroom": "Bedroom", "kamar": "Bedroom",
        "kitchen": "Kitchen", "dapur": "Kitchen",
        "office": "Office", "kantor": "Office",
    }

    target_device = None
    target_type = None
    target_room = None

    for keyword, dtype in device_map.items():
        if keyword in text:
            target_type = dtype
            break

    for keyword, room in room_map.items():
        if keyword in text:
            target_room = room
            break

    if target_type and (is_on or is_off):
        # Build device ID hint
        room_prefix = {"Living Room": "lr", "Bedroom": "br", "Kitchen": "kt", "Office": "of"}.get(target_room, "")
        type_prefix = {"light": "light", "ac": "ac", "fan": "fan", "lock": "lock"}.get(target_type, "")

        return {
            "action": "control",
            "device_id": f"{room_prefix}_{type_prefix}" if room_prefix else target_type,
            "command": "on" if is_on else "off",
            "params": {"device_type": target_type, "room": target_room},
            "response": f"✅ {'Menyalakan' if is_on else 'Mematikan'} {target_type} di {target_room or 'semua ruangan'}!",
        }

    # Temperature set
    import re
    temp_match = re.search(r'(\d{2})\s*(?:°|derajat|degree|c)', text)
    if temp_match and ("ac" in text or "temperature" in text or "suhu" in text):
        temp = int(temp_match.group(1))
        return {
            "action": "control",
            "device_id": "ac",
            "command": "set",
            "params": {"temperature": temp},
            "response": f"✅ Suhu AC diatur ke {temp}°C!",
        }

    return {
        "action": "unknown",
        "device_id": None,
        "command": None,
        "params": {},
        "response": "🤔 Perintah tidak dimengerti. Coba: 'turn on living room light' atau 'good night'",
    }


def build_device_context(devices) -> str:
    """Build device context string for MIMO prompt."""
    lines = []
    for d in devices:
        status = "ON" if d.is_on else "OFF"
        lines.append(f"- {d.id}: {d.name} ({d.device_type}) in {d.room} [{status}]")
    return "\n".join(lines)
