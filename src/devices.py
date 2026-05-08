"""
🏠 Xiaomi Smart Home Bot — Device Database
Simulated IoT devices with real-time state management.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "smarthome.db"


class DeviceType(Enum):
    LIGHT = "light"
    AC = "ac"
    FAN = "fan"
    PLUG = "plug"
    LOCK = "lock"
    SENSOR = "sensor"


class Room(Enum):
    LIVING = "Living Room"
    BEDROOM = "Bedroom"
    KITCHEN = "Kitchen"
    BATHROOM = "Bathroom"
    OFFICE = "Office"
    GARAGE = "Garage"


@dataclass
class SmartDevice:
    id: str
    name: str
    device_type: str
    room: str
    is_on: bool = False
    # Light params
    brightness: int = 100  # 0-100
    color_temp: int = 4000  # Kelvin (2700-6500)
    # AC params
    temperature: int = 24  # Celsius
    mode: str = "cool"  # cool/heat/dry/fan
    fan_speed: str = "auto"  # low/med/high/auto
    # Fan params
    speed: int = 1  # 1-3
    oscillation: bool = False
    # Plug params
    power_watts: float = 0.0
    energy_kwh: float = 0.0
    # Lock params
    is_locked: bool = True
    # Sensor params
    sensor_temp: float = 28.0
    sensor_humidity: int = 65
    # Common
    last_updated: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)

    def status_text(self) -> str:
        icons = {
            "light": "💡",
            "ac": "❄️",
            "fan": "🌀",
            "plug": "🔌",
            "lock": "🔒",
            "sensor": "🌡️",
        }
        icon = icons.get(self.device_type, "📱")
        status = "🟢 ON" if self.is_on else "⚫ OFF"

        if self.device_type == "light":
            return f"{icon} {self.name} [{status}] {self.brightness}% | {self.color_temp}K"
        elif self.device_type == "ac":
            return f"{icon} {self.name} [{status}] {self.temperature}°C | {self.mode} | {self.fan_speed}"
        elif self.device_type == "fan":
            osc = "🔄" if self.oscillation else "⏸️"
            return f"{icon} {self.name} [{status}] Speed {self.speed}/3 {osc}"
        elif self.device_type == "plug":
            return f"{icon} {self.name} [{status}] {self.power_watts:.0f}W | {self.energy_kwh:.1f}kWh"
        elif self.device_type == "lock":
            lock_status = "🔒 LOCKED" if self.is_locked else "🔓 UNLOCKED"
            return f"{icon} {self.name} [{lock_status}]"
        elif self.device_type == "sensor":
            return f"{icon} {self.name} 🌡️{self.sensor_temp:.1f}°C 💧{self.sensor_humidity}%"
        return f"{icon} {self.name} [{status}]"


class DeviceDB:
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self._seed_devices()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                room TEXT NOT NULL,
                state_json TEXT NOT NULL,
                created_at REAL DEFAULT (unixepoch()),
                updated_at REAL DEFAULT (unixepoch())
            );

            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                action TEXT NOT NULL,
                cron_expr TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at REAL DEFAULT (unixepoch())
            );

            CREATE TABLE IF NOT EXISTS energy_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                watts REAL NOT NULL,
                timestamp REAL DEFAULT (unixepoch())
            );

            CREATE TABLE IF NOT EXISTS scenes (
                name TEXT PRIMARY KEY,
                devices_json TEXT NOT NULL,
                description TEXT
            );
        """)
        self.conn.commit()

    def _seed_devices(self):
        """Initialize default smart home devices."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM devices")
        if cursor.fetchone()[0] > 0:
            return

        devices = [
            # Living Room
            SmartDevice("lr_light_1", "Main Light", "light", "Living Room", is_on=True, brightness=80, color_temp=4000),
            SmartDevice("lr_light_2", "Ambient Strip", "light", "Living Room", is_on=False, brightness=50, color_temp=3000),
            SmartDevice("lr_ac", "Air Conditioner", "ac", "Living Room", is_on=True, temperature=24, mode="cool", fan_speed="auto"),
            SmartDevice("lr_fan", "Ceiling Fan", "fan", "Living Room", is_on=False, speed=2, oscillation=True),
            SmartDevice("lr_plug_tv", "TV Plug", "plug", "Living Room", is_on=True, power_watts=120, energy_kwh=2.4),
            SmartDevice("lr_sensor", "Environment Sensor", "sensor", "Living Room", sensor_temp=28.5, sensor_humidity=65),

            # Bedroom
            SmartDevice("br_light_1", "Bedroom Light", "light", "Bedroom", is_on=False, brightness=100, color_temp=3500),
            SmartDevice("br_ac", "Bedroom AC", "ac", "Bedroom", is_on=False, temperature=26, mode="cool", fan_speed="low"),
            SmartDevice("br_fan", "Standing Fan", "fan", "Bedroom", is_on=True, speed=1, oscillation=False),
            SmartDevice("br_sensor", "Environment Sensor", "sensor", "Bedroom", sensor_temp=27.2, sensor_humidity=70),

            # Kitchen
            SmartDevice("kt_light_1", "Kitchen Light", "light", "Kitchen", is_on=True, brightness=100, color_temp=5000),
            SmartDevice("kt_plug_fridge", "Smart Fridge", "plug", "Kitchen", is_on=True, power_watts=150, energy_kwh=8.2),
            SmartDevice("kt_sensor", "Environment Sensor", "sensor", "Kitchen", sensor_temp=30.1, sensor_humidity=55),

            # Office
            SmartDevice("of_light_1", "Desk Lamp", "light", "Office", is_on=True, brightness=90, color_temp=5500),
            SmartDevice("of_plug_pc", "PC Setup", "plug", "Office", is_on=True, power_watts=350, energy_kwh=5.1),
            SmartDevice("of_sensor", "Environment Sensor", "sensor", "Office", sensor_temp=26.8, sensor_humidity=60),

            # Door Locks
            SmartDevice("front_lock", "Front Door", "lock", "Living Room", is_locked=True),
            SmartDevice("back_lock", "Back Door", "lock", "Kitchen", is_locked=True),
        ]

        for d in devices:
            self.conn.execute(
                "INSERT INTO devices (id, name, device_type, room, state_json) VALUES (?, ?, ?, ?, ?)",
                (d.id, d.name, d.device_type, d.room, json.dumps(d.to_dict()))
            )

        # Seed scenes
        scenes = {
            "movie": {"name": "🎬 Movie Mode", "desc": "Dim lights, AC cool, TV on", "devices": {
                "lr_light_1": {"is_on": True, "brightness": 20},
                "lr_light_2": {"is_on": True, "brightness": 30, "color_temp": 2700},
                "lr_ac": {"is_on": True, "temperature": 24},
                "lr_plug_tv": {"is_on": True},
            }},
            "sleep": {"name": "😴 Sleep Mode", "desc": "All lights off, AC auto, fan low", "devices": {
                "lr_light_1": {"is_on": False},
                "lr_light_2": {"is_on": False},
                "br_light_1": {"is_on": False},
                "br_ac": {"is_on": True, "temperature": 26, "fan_speed": "low"},
                "br_fan": {"is_on": True, "speed": 1},
                "front_lock": {"is_locked": True},
                "back_lock": {"is_locked": True},
            }},
            "away": {"name": "🏖️ Away Mode", "desc": "Everything off, doors locked", "devices": {
                "lr_light_1": {"is_on": False},
                "lr_light_2": {"is_on": False},
                "lr_ac": {"is_on": False},
                "br_light_1": {"is_on": False},
                "br_ac": {"is_on": False},
                "kt_light_1": {"is_on": False},
                "of_light_1": {"is_on": False},
                "front_lock": {"is_locked": True},
                "back_lock": {"is_locked": True},
            }},
            "party": {"name": "🎉 Party Mode", "desc": "Colorful lights, AC cold, music", "devices": {
                "lr_light_1": {"is_on": True, "brightness": 100, "color_temp": 3000},
                "lr_light_2": {"is_on": True, "brightness": 100, "color_temp": 2700},
                "lr_ac": {"is_on": True, "temperature": 20},
                "lr_fan": {"is_on": True, "speed": 3},
                "lr_plug_tv": {"is_on": True},
            }},
            "morning": {"name": "🌅 Good Morning", "desc": "Bright lights, AC comfortable", "devices": {
                "lr_light_1": {"is_on": True, "brightness": 80, "color_temp": 5000},
                "kt_light_1": {"is_on": True, "brightness": 100},
                "of_light_1": {"is_on": True, "brightness": 90},
                "lr_ac": {"is_on": True, "temperature": 25},
            }},
        }

        for key, scene in scenes.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO scenes (name, devices_json, description) VALUES (?, ?, ?)",
                (key, json.dumps(scene["devices"]), f"{scene['name']} — {scene['desc']}")
            )

        self.conn.commit()

    def get_all_devices(self) -> list[SmartDevice]:
        rows = self.conn.execute("SELECT state_json FROM devices ORDER BY room, name").fetchall()
        return [SmartDevice(**json.loads(r["state_json"])) for r in rows]

    def get_device(self, device_id: str) -> Optional[SmartDevice]:
        row = self.conn.execute("SELECT state_json FROM devices WHERE id = ?", (device_id,)).fetchone()
        if row:
            return SmartDevice(**json.loads(row["state_json"]))
        return None

    def update_device(self, device: SmartDevice):
        device.last_updated = time.time()
        self.conn.execute(
            "UPDATE devices SET state_json = ?, updated_at = unixepoch() WHERE id = ?",
            (json.dumps(device.to_dict()), device.id)
        )
        self.conn.commit()

    def get_devices_by_room(self, room: str) -> list[SmartDevice]:
        rows = self.conn.execute("SELECT state_json FROM devices WHERE room = ? ORDER BY name", (room,)).fetchall()
        return [SmartDevice(**json.loads(r["state_json"])) for r in rows]

    def get_rooms(self) -> list[str]:
        rows = self.conn.execute("SELECT DISTINCT room FROM devices ORDER BY room").fetchall()
        return [r["room"] for r in rows]

    def get_scene(self, scene_name: str) -> Optional[dict]:
        row = self.conn.execute("SELECT devices_json, description FROM scenes WHERE name = ?", (scene_name,)).fetchone()
        if row:
            return {"devices": json.loads(row["devices_json"]), "description": row["description"]}
        return None

    def get_all_scenes(self) -> list[dict]:
        rows = self.conn.execute("SELECT name, description FROM scenes").fetchall()
        return [{"name": r["name"], "description": r["description"]} for r in rows]

    def apply_scene(self, scene_name: str) -> list[str]:
        scene = self.get_scene(scene_name)
        if not scene:
            return []

        changes = []
        for dev_id, props in scene["devices"].items():
            device = self.get_device(dev_id)
            if device:
                for key, val in props.items():
                    setattr(device, key, val)
                self.update_device(device)
                changes.append(device.status_text())
        return changes

    def get_total_power(self) -> float:
        devices = self.get_all_devices()
        return sum(d.power_watts for d in devices if d.device_type == "plug" and d.is_on)

    def get_energy_report(self) -> dict:
        devices = self.get_all_devices()
        plugs = [d for d in devices if d.device_type == "plug"]
        return {
            "total_power_watts": sum(d.power_watts for d in plugs if d.is_on),
            "total_energy_kwh": sum(d.energy_kwh for d in plugs),
            "active_devices": sum(1 for d in devices if d.is_on),
            "total_devices": len(devices),
            "plugs": [{"name": d.name, "watts": d.power_watts, "kwh": d.energy_kwh} for d in plugs],
        }

    def close(self):
        self.conn.close()
