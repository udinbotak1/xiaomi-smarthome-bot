"""
🏠 Xiaomi Smart Home Bot — Telegram Interface
AI-powered smart home controller via Telegram.
"""

import os
import sys
import json
import logging
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from devices import DeviceDB, SmartDevice, DeviceType
from mimo_ai import get_mimo_response, build_device_context, parse_command_fallback

# ── Config ──────────────────────────────────────────────────
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
db = DeviceDB()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────────

def room_keyboard():
    rooms = db.get_rooms()
    keyboard = [[InlineKeyboardButton(f"🏠 {r}", callback_data=f"room:{r}")] for r in rooms]
    keyboard.append([InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")])
    return InlineKeyboardMarkup(keyboard)


def device_keyboard(devices: list[SmartDevice]):
    keyboard = []
    for d in devices:
        icon = {"light": "💡", "ac": "❄️", "fan": "🌀", "plug": "🔌", "lock": "🔒", "sensor": "🌡️"}
        status = "🟢" if (d.is_on or (d.device_type == "lock" and d.is_locked)) else "⚫"
        btn_text = f"{icon.get(d.device_type, '📱')} {d.name} {status}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"device:{d.id}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back to Rooms", callback_data="rooms")])
    return InlineKeyboardMarkup(keyboard)


def device_controls(device: SmartDevice):
    keyboard = []
    if device.device_type == "light":
        keyboard.append([
            InlineKeyboardButton("💡 ON", callback_data=f"ctrl:{device.id}:on"),
            InlineKeyboardButton("⚫ OFF", callback_data=f"ctrl:{device.id}:off"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔅 25%", callback_data=f"ctrl:{device.id}:bright:25"),
            InlineKeyboardButton("🔆 50%", callback_data=f"ctrl:{device.id}:bright:50"),
            InlineKeyboardButton("☀️ 100%", callback_data=f"ctrl:{device.id}:bright:100"),
        ])
        keyboard.append([
            InlineKeyboardButton("🌅 Warm", callback_data=f"ctrl:{device.id}:temp:2700"),
            InlineKeyboardButton("☀️ Neutral", callback_data=f"ctrl:{device.id}:temp:4000"),
            InlineKeyboardButton("❄️ Cool", callback_data=f"ctrl:{device.id}:temp:6500"),
        ])
    elif device.device_type == "ac":
        keyboard.append([
            InlineKeyboardButton("❄️ ON", callback_data=f"ctrl:{device.id}:on"),
            InlineKeyboardButton("⚫ OFF", callback_data=f"ctrl:{device.id}:off"),
        ])
        keyboard.append([
            InlineKeyboardButton("🌡️ -1°", callback_data=f"ctrl:{device.id}:temp_down"),
            InlineKeyboardButton(f"{device.temperature}°C", callback_data=f"ctrl:{device.id}:noop"),
            InlineKeyboardButton("🌡️ +1°", callback_data=f"ctrl:{device.id}:temp_up"),
        ])
        keyboard.append([
            InlineKeyboardButton("❄️ Cool", callback_data=f"ctrl:{device.id}:mode:cool"),
            InlineKeyboardButton("🔥 Heat", callback_data=f"ctrl:{device.id}:mode:heat"),
            InlineKeyboardButton("💨 Fan", callback_data=f"ctrl:{device.id}:mode:fan"),
        ])
    elif device.device_type == "fan":
        keyboard.append([
            InlineKeyboardButton("🌀 ON", callback_data=f"ctrl:{device.id}:on"),
            InlineKeyboardButton("⚫ OFF", callback_data=f"ctrl:{device.id}:off"),
        ])
        keyboard.append([
            InlineKeyboardButton("💨 Low", callback_data=f"ctrl:{device.id}:speed:1"),
            InlineKeyboardButton("💨💨 Med", callback_data=f"ctrl:{device.id}:speed:2"),
            InlineKeyboardButton("💨💨💨 High", callback_data=f"ctrl:{device.id}:speed:3"),
        ])
    elif device.device_type == "plug":
        keyboard.append([
            InlineKeyboardButton("🔌 ON", callback_data=f"ctrl:{device.id}:on"),
            InlineKeyboardButton("⚫ OFF", callback_data=f"ctrl:{device.id}:off"),
        ])
    elif device.device_type == "lock":
        keyboard.append([
            InlineKeyboardButton("🔒 Lock", callback_data=f"ctrl:{device.id}:lock"),
            InlineKeyboardButton("🔓 Unlock", callback_data=f"ctrl:{device.id}:unlock"),
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"room:{device.room}")])
    return InlineKeyboardMarkup(keyboard)


# ── Commands ────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏠 *Xiaomi Smart Home Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Kontrol rumah pintar lu lewat Telegram!\n\n"
        "📌 *Commands:*\n"
        "/devices — Semua perangkat\n"
        "/rooms — Browse by ruangan\n"
        "/scenes — Mode otomatis\n"
        "/dashboard — Status real-time\n"
        "/voice <cmd> — AI voice command\n"
        "/energy — Laporan daya\n\n"
        "🤖 *AI Commands:*\n"
        "Ketik langsung aja, misal:\n"
        "• \"turn on bedroom light\"\n"
        "• \"set AC to 22 degrees\"\n"
        "• \"good night\"\n"
        "• \"how much power am I using?\""
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=room_keyboard())


async def devices_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    all_devices = db.get_all_devices()
    rooms = db.get_rooms()

    text = "🏠 *All Smart Devices*\n━━━━━━━━━━━━━━━━\n\n"
    current_room = ""
    for d in all_devices:
        if d.room != current_room:
            current_room = d.room
            text += f"\n*{current_room}*\n"
        text += f"  {d.status_text()}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def rooms_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 *Pilih Ruangan:*",
        parse_mode="Markdown",
        reply_markup=room_keyboard()
    )


async def dashboard_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = build_dashboard()
    await update.message.reply_text(text, parse_mode="Markdown")


async def scenes_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    scenes = db.get_all_scenes()
    keyboard = []
    for s in scenes:
        keyboard.append([InlineKeyboardButton(s["description"], callback_data=f"scene:{s['name']}")])

    await update.message.reply_text(
        "🎭 *Scene Modes*\n━━━━━━━━━━━━\nPilih mode otomatis:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def energy_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    report = db.get_energy_report()
    text = (
        "⚡ *Power Consumption Report*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔌 Active devices: {report['active_devices']}/{report['total_devices']}\n"
        f"⚡ Current draw: {report['total_power_watts']:.0f}W\n"
        f"🔋 Total energy: {report['total_energy_kwh']:.1f} kWh\n\n"
        "*Top consumers:*\n"
    )
    sorted_plugs = sorted(report["plugs"], key=lambda x: x["watts"], reverse=True)
    for i, p in enumerate(sorted_plugs[:5], 1):
        text += f"{i}. {p['name']} — {p['watts']:.0f}W ({p['kwh']:.1f}kWh)\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def voice_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("🎤 Ketik perintah setelah /voice\nContoh: /voice turn on living room light")
        return

    command_text = " ".join(ctx.args)
    await handle_ai_command(update, command_text)


async def handle_ai_command(update: Update, text: str):
    devices = db.get_all_devices()
    context = build_device_context(devices)

    # Try MIMO API first, fallback to keyword parser
    api_key = os.environ.get("MIMO_API_KEY", "")
    if api_key:
        result = get_mimo_response(text, context)
    else:
        result = parse_command_fallback(text)

    response = result.get("response", "🤔 Tidak dimengerti")
    action = result.get("action")

    if action == "control":
        device_id = result.get("device_id", "")
        command = result.get("command", "")
        params = result.get("params", {})

        # Find matching device
        matched = None
        for d in devices:
            if device_id and device_id in d.id:
                matched = d
                break
            if params.get("device_type") == d.device_type:
                if params.get("room") and params["room"] in d.room:
                    matched = d
                    break
                elif not params.get("room"):
                    matched = d
                    break

        if matched:
            if command == "on":
                matched.is_on = True
            elif command == "off":
                matched.is_on = False
            elif command == "set":
                for k, v in params.items():
                    if hasattr(matched, k):
                        setattr(matched, k, v)
            db.update_device(matched)
            response += f"\n\n{matched.status_text()}"

    elif action == "scene":
        scene_name = result.get("command", "")
        changes = db.apply_scene(scene_name)
        if changes:
            response += "\n\n" + "\n".join(changes)

    elif action == "query":
        report = db.get_energy_report()
        response = (
            f"⚡ *Power Status*\n\n"
            f"Current draw: {report['total_power_watts']:.0f}W\n"
            f"Active devices: {report['active_devices']}/{report['total_devices']}\n"
            f"Total energy: {report['total_energy_kwh']:.1f} kWh"
        )

    await update.message.reply_text(response, parse_mode="Markdown")


async def ai_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle any text message as AI command."""
    text = update.message.text
    if text.startswith("/"):
        return
    await handle_ai_command(update, text)


# ── Callbacks ───────────────────────────────────────────────

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "rooms" or data == "dashboard":
        if data == "dashboard":
            text = build_dashboard()
            await query.edit_message_text(text, parse_mode="Markdown")
        else:
            await query.edit_message_text(
                "🏠 *Pilih Ruangan:*",
                parse_mode="Markdown",
                reply_markup=room_keyboard()
            )

    elif data.startswith("room:"):
        room = data.split(":", 1)[1]
        devices = db.get_devices_by_room(room)
        text = f"🏠 *{room}*\n━━━━━━━━━━━━━━\n\n"
        for d in devices:
            text += f"{d.status_text()}\n"
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=device_keyboard(devices)
        )

    elif data.startswith("device:"):
        dev_id = data.split(":", 1)[1]
        device = db.get_device(dev_id)
        if device:
            text = f"🎛️ *{device.name}*\n━━━━━━━━━━━━━━\n\n{device.status_text()}"
            await query.edit_message_text(
                text, parse_mode="Markdown",
                reply_markup=device_controls(device)
            )

    elif data.startswith("ctrl:"):
        parts = data.split(":")
        dev_id = parts[1]
        action = parts[2]
        device = db.get_device(dev_id)
        if not device:
            await query.answer("Device not found!")
            return

        if action == "on":
            device.is_on = True
        elif action == "off":
            device.is_on = False
        elif action == "bright" and len(parts) > 3:
            device.brightness = int(parts[3])
        elif action == "temp" and len(parts) > 3:
            device.color_temp = int(parts[3])
        elif action == "temp_up":
            device.temperature = min(30, device.temperature + 1)
        elif action == "temp_down":
            device.temperature = max(16, device.temperature - 1)
        elif action == "mode" and len(parts) > 3:
            device.mode = parts[3]
        elif action == "speed" and len(parts) > 3:
            device.speed = int(parts[3])
        elif action == "lock":
            device.is_locked = True
        elif action == "unlock":
            device.is_locked = False

        db.update_device(device)
        text = f"🎛️ *{device.name}*\n━━━━━━━━━━━━━━\n\n{device.status_text()}\n\n✅ Updated!"
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=device_controls(device)
        )

    elif data.startswith("scene:"):
        scene_name = data.split(":", 1)[1]
        changes = db.apply_scene(scene_name)
        text = f"🎭 *Scene Applied!*\n\n" + "\n".join(changes)
        await query.edit_message_text(text, parse_mode="Markdown")


# ── Dashboard Builder ───────────────────────────────────────

def build_dashboard() -> str:
    devices = db.get_all_devices()
    rooms = db.get_rooms()
    report = db.get_energy_report()

    text = "📊 *Smart Home Dashboard*\n━━━━━━━━━━━━━━━━━━━━\n\n"

    for room in rooms:
        room_devs = [d for d in devices if d.room == room]
        text += f"*{room}*\n"
        for d in room_devs:
            text += f"  {d.status_text()}\n"
        text += "\n"

    text += (
        f"⚡ *Power:* {report['total_power_watts']:.0f}W | "
        f"🔋 {report['total_energy_kwh']:.1f}kWh\n"
        f"📱 *Active:* {report['active_devices']}/{report['total_devices']} devices"
    )
    return text


# ── Main ────────────────────────────────────────────────────

def main():
    if not TOKEN:
        print("❌ Set TELEGRAM_BOT_TOKEN environment variable!")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token'")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("devices", devices_cmd))
    app.add_handler(CommandHandler("rooms", rooms_cmd))
    app.add_handler(CommandHandler("dashboard", dashboard_cmd))
    app.add_handler(CommandHandler("scenes", scenes_cmd))
    app.add_handler(CommandHandler("energy", energy_cmd))
    app.add_handler(CommandHandler("voice", voice_cmd))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    # AI message handler (any text)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_message))

    print("🏠 Xiaomi Smart Home Bot started!")
    print("   Press Ctrl+C to stop")
    app.run_polling()


if __name__ == "__main__":
    main()
