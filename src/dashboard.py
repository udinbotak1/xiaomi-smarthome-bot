"""
📊 Smart Home Dashboard — Web UI
Visual dashboard for screenshots and demo.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from devices import DeviceDB

db = DeviceDB()


def generate_dashboard_html():
    devices = db.get_all_devices()
    rooms = db.get_rooms()
    report = db.get_energy_report()

    # Build device cards by room
    room_sections = ""
    for room in rooms:
        room_devs = [d for d in devices if d.room == room]
        cards = ""
        for d in room_devs:
            status_class = "on" if d.is_on or (d.device_type == "lock" and d.is_locked) else "off"
            icon = {"light": "💡", "ac": "❄️", "fan": "🌀", "plug": "🔌", "lock": "🔒", "sensor": "🌡️"}.get(d.device_type, "📱")

            detail = ""
            if d.device_type == "light":
                detail = f"{d.brightness}% | {d.color_temp}K"
            elif d.device_type == "ac":
                detail = f"{d.temperature}°C | {d.mode}"
            elif d.device_type == "fan":
                detail = f"Speed {d.speed}/3"
            elif d.device_type == "plug":
                detail = f"{d.power_watts:.0f}W"
            elif d.device_type == "lock":
                detail = "Locked" if d.is_locked else "Unlocked"
                status_class = "locked" if d.is_locked else "unlocked"
            elif d.device_type == "sensor":
                detail = f"{d.sensor_temp:.1f}°C | {d.sensor_humidity}%"

            cards += f"""
            <div class="device-card {status_class}">
                <div class="device-icon">{icon}</div>
                <div class="device-info">
                    <div class="device-name">{d.name}</div>
                    <div class="device-detail">{detail}</div>
                </div>
                <div class="device-status {'active' if status_class == 'on' or status_class == 'locked' else 'inactive'}">
                    {'ON' if status_class in ('on', 'locked') else 'OFF'}
                </div>
            </div>"""

        room_sections += f"""
        <div class="room-section">
            <h2>🏠 {room}</h2>
            <div class="device-grid">{cards}</div>
        </div>"""

    # Energy bar
    plugs = [d for d in devices if d.device_type == "plug"]
    energy_bars = ""
    max_watts = max((p.power_watts for p in plugs), default=1)
    for p in sorted(plugs, key=lambda x: x.power_watts, reverse=True):
        pct = (p.power_watts / max_watts * 100) if max_watts > 0 else 0
        energy_bars += f"""
        <div class="energy-bar">
            <div class="energy-label">{p.name}</div>
            <div class="energy-track">
                <div class="energy-fill" style="width: {pct}%"></div>
            </div>
            <div class="energy-value">{p.power_watts:.0f}W</div>
        </div>"""

    now = datetime.now().strftime("%H:%M — %d %B %Y")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🏠 Xiaomi Smart Home Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'SF Pro', -apple-system, sans-serif;
    background: #0a0a0f;
    color: #e0e0e0;
    min-height: 100vh;
  }}
  .header {{
    background: linear-gradient(135deg, #ff6900 0%, #ff4500 100%);
    padding: 30px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .header h1 {{ font-size: 28px; color: white; }}
  .header .time {{ color: rgba(255,255,255,0.8); font-size: 14px; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}

  /* Stats Bar */
  .stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 30px;
  }}
  .stat-card {{
    background: #1a1a2e;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #2a2a4a;
  }}
  .stat-card .label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
  .stat-card .value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .stat-card .value.orange {{ color: #ff6900; }}
  .stat-card .value.green {{ color: #00d26a; }}
  .stat-card .value.blue {{ color: #4da6ff; }}
  .stat-card .value.red {{ color: #ff4757; }}

  /* Room Sections */
  .room-section {{
    margin-bottom: 30px;
  }}
  .room-section h2 {{
    font-size: 18px;
    margin-bottom: 12px;
    color: #ccc;
    border-bottom: 1px solid #2a2a4a;
    padding-bottom: 8px;
  }}
  .device-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
  }}
  .device-card {{
    background: #1a1a2e;
    border-radius: 10px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border: 1px solid #2a2a4a;
    transition: all 0.2s;
  }}
  .device-card:hover {{ border-color: #ff6900; }}
  .device-card.on {{ border-left: 3px solid #00d26a; }}
  .device-card.off {{ border-left: 3px solid #444; }}
  .device-card.locked {{ border-left: 3px solid #4da6ff; }}
  .device-card.unlocked {{ border-left: 3px solid #ff4757; }}
  .device-icon {{ font-size: 28px; }}
  .device-info {{ flex: 1; }}
  .device-name {{ font-weight: 600; font-size: 14px; }}
  .device-detail {{ color: #888; font-size: 12px; margin-top: 2px; }}
  .device-status {{
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
  }}
  .device-status.active {{ background: rgba(0,210,106,0.2); color: #00d26a; }}
  .device-status.inactive {{ background: rgba(100,100,100,0.2); color: #666; }}

  /* Energy Section */
  .energy-section {{
    background: #1a1a2e;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #2a2a4a;
    margin-top: 30px;
  }}
  .energy-section h2 {{ font-size: 18px; margin-bottom: 16px; }}
  .energy-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }}
  .energy-label {{ width: 120px; font-size: 13px; color: #aaa; }}
  .energy-track {{
    flex: 1;
    height: 8px;
    background: #2a2a4a;
    border-radius: 4px;
    overflow: hidden;
  }}
  .energy-fill {{
    height: 100%;
    background: linear-gradient(90deg, #ff6900, #ff4500);
    border-radius: 4px;
    transition: width 0.5s;
  }}
  .energy-value {{ width: 60px; text-align: right; font-size: 13px; color: #ff6900; }}

  .footer {{
    text-align: center;
    padding: 20px;
    color: #555;
    font-size: 12px;
  }}
</style>
</head>
<body>
<div class="header">
    <h1>🏠 Xiaomi Smart Home</h1>
    <div class="time">{now}</div>
</div>
<div class="container">
    <div class="stats">
        <div class="stat-card">
            <div class="label">Active Devices</div>
            <div class="value orange">{report['active_devices']}</div>
        </div>
        <div class="stat-card">
            <div class="label">Power Draw</div>
            <div class="value green">{report['total_power_watts']:.0f}W</div>
        </div>
        <div class="stat-card">
            <div class="label">Energy Today</div>
            <div class="value blue">{report['total_energy_kwh']:.1f} kWh</div>
        </div>
        <div class="stat-card">
            <div class="label">Total Devices</div>
            <div class="value red">{report['total_devices']}</div>
        </div>
    </div>

    {room_sections}

    <div class="energy-section">
        <h2>⚡ Power Consumption</h2>
        {energy_bars}
    </div>
</div>
<div class="footer">
    Xiaomi Smart Home Bot — Powered by Xiaomi MIMO AI
</div>
</body>
</html>"""
    return html


if __name__ == "__main__":
    html = generate_dashboard_html()
    output = Path(__file__).parent.parent / "assets" / "dashboard.html"
    output.parent.mkdir(exist_ok=True)
    output.write_text(html)
    print(f"✅ Dashboard generated: {output}")
