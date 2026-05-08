# 🏠 Xiaomi Smart Home Bot

> AI-powered smart home controller powered by Xiaomi MIMO

Control your smart home devices through Telegram with AI assistance. Monitor temperature, manage lights, schedule automation, and more — all through a conversational interface.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Xiaomi MIMO](https://img.shields.io/badge/AI-Xiaomi%20MIMO-orange)

## ✨ Features

### 🎛️ Device Control
- **Smart Lights** — ON/OFF, brightness, color temperature
- **Air Conditioner** — Mode, temperature, fan speed
- **Smart Fan** — Speed levels, oscillation, timer
- **Smart Plug** — Power monitoring, remote control
- **Door Lock** — Lock/unlock status, access logs

### 📊 Real-time Monitoring
- **Temperature & Humidity** sensors per room
- **Power consumption** tracking (Watts, kWh)
- **Device status** dashboard
- **Historical data** charts

### 🤖 AI Features (Xiaomi MIMO)
- **Voice command** simulation ("turn off bedroom lights")
- **Smart suggestions** — "It's hot, turn on AC?"
- **Energy optimization** tips
- **Routine automation** — "Good morning" / "Good night"

### ⏰ Automation
- **Scheduled tasks** — Turn on lights at 6 PM
- **Conditional rules** — If temp > 30°C, turn on AC
- **Scene modes** — Movie, Sleep, Away, Party

## 🛠️ Tech Stack

- **Python 3.10+** — Core language
- **python-telegram-bot** — Telegram Bot API
- **Xiaomi MIMO API** — AI command processing
- **SQLite** — Device state & history
- **APScheduler** — Task scheduling
- **Rich** — Terminal UI for monitoring

## 📦 Installation

```bash
# Clone repo
git clone https://github.com/periomo/xiaomi-smarthome-bot.git
cd xiaomi-smarthome-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export MIMO_API_KEY="your_mimo_api_key"

# Run the bot
python src/bot.py
```

## 🚀 Usage

### Telegram Commands

```
/start          — Welcome & device overview
/devices        — List all smart devices
/rooms          — Browse by room
/schedule       — Manage automation schedules
/scenes         — Activate scene modes
/dashboard      — Real-time status dashboard
/voice <cmd>    — AI voice command
/energy         — Power consumption report
/help           — All commands
```

### AI Voice Commands

```
/voice turn on living room lights
/voice set AC to 24 degrees
/voice good night mode
/voice how much power am I using?
/voice is the front door locked?
```

### Scene Modes

| Scene    | Lights | AC   | Fan  | Plug |
|----------|--------|------|------|------|
| 🎬 Movie | Dim 20%| 24°C | OFF  | ON   |
| 😴 Sleep | OFF    | 26°C | Low  | OFF  |
| 🏖️ Away  | OFF    | OFF  | OFF  | OFF  |
| 🎉 Party | Color  | 22°C | High | ON   |
| 🌅 Morning| 80%   | 25°C | Med  | ON   |

## 📸 Screenshots

### Device Control
```
┌─────────────────────────────────┐
│  🏠 Living Room                 │
│                                 │
│  💡 Main Light    [ON]  80%     │
│  ❄️  AC            [ON]  24°C   │
│  🌀 Fan           [OFF]         │
│  🔌 TV Plug       [ON]  120W    │
│  🌡️ Temperature   28.5°C        │
│  💧 Humidity      65%           │
└─────────────────────────────────┘
```

### Energy Dashboard
```
┌─────────────────────────────────┐
│  ⚡ Power Consumption           │
│                                 │
│  Today:    12.4 kWh  ▼5%        │
│  This week: 87.2 kWh            │
│  Monthly:  342.1 kWh            │
│                                 │
│  Top consumers:                 │
│  1. AC Living    — 4.2 kWh      │
│  2. AC Bedroom   — 3.8 kWh      │
│  3. Water Heater — 2.1 kWh      │
└─────────────────────────────────┘
```

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Telegram   │────▶│  Smart Home  │────▶│   Xiaomi     │
│   Bot        │◀────│  Controller  │◀────│   MIMO API   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                    ┌───────┴───────┐
                    │   SQLite DB   │
                    │  (devices,    │
                    │   schedules,  │
                    │   history)    │
                    └───────────────┘
```

## 📄 License

MIT License — feel free to use and modify.

## 👤 Author

**udinbotak1** — [github.com/udinbotak1](https://github.com/udinbotak1)

---

*Built with ❤️ for Xiaomi MIMO Application*
