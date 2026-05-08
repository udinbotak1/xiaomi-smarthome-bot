"""
🎬 Generate demo video for Xiaomi Smart Home Bot
Animated terminal-style demo showing bot interactions.
"""

import os
import sys
import subprocess

# Check available tools
def generate_video():
    output_path = "/root/xiaomi-smarthome-bot/assets/demo_smarthome.mp4"
    
    # Use ffmpeg to create a simple animated demo from frames
    # We'll create frames using PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        os.system("pip install Pillow -q")
        from PIL import Image, ImageDraw, ImageFont

    W, H = 640, 360
    FPS = 15
    frames = []
    
    # Colors
    BG = (10, 10, 15)
    ORANGE = (255, 105, 0)
    GREEN = (0, 210, 106)
    WHITE = (240, 240, 240)
    GRAY = (136, 136, 136)
    DARK = (26, 26, 46)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except:
        font = ImageFont.load_default()
        font_sm = font
        font_title = font

    def draw_frame(lines, title="🏠 Xiaomi Smart Home Bot"):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        
        # Header
        d.rectangle([0, 0, W, 40], fill=(255, 105, 0))
        d.text((20, 10), title, fill=WHITE, font=font_title)
        d.text((W-140, 12), "Powered by MiMo", fill=(255, 255, 255), font=font_sm)
        
        # Content
        y = 55
        for line, color in lines:
            d.text((20, y), line, fill=color, font=font)
            y += 22
        
        return img

    # Scene 1: Welcome
    scenes = [
        # (lines, duration_seconds)
        (
            [("$ /start", ORANGE), ("", WHITE),
             ("🏠 Xiaomi Smart Home Bot", WHITE),
             ("━━━━━━━━━━━━━━━━━━━━━━", GRAY),
             ("Kontrol rumah pintar lewat Telegram!", WHITE),
             ("", WHITE),
             ("🏠 Living Room  - 5 devices", GREEN),
             ("🛏️  Bedroom     - 4 devices", GREEN),
             ("🍳 Kitchen     - 3 devices", GREEN),
             ("💻 Office      - 3 devices", GREEN),
             ("🔒 2 Door Locks", GREEN)],
            2.5
        ),
        # Scene 2: Voice command
        (
            [("$ /voice turn on living room light", ORANGE), ("", WHITE),
             ("🧠 MiMo: 'Menyalakan lampu ruang tamu!'", WHITE),
             ("", WHITE),
             ("✅ Living Room Light → ON", GREEN),
             ("   💡 Main Light [ON] 80% | 4000K", WHITE),
             ("   🌡️ 28.5°C | 💧 65%", GRAY),
             ("", WHITE),
             ("✅ Device updated successfully!", GREEN)],
            2.5
        ),
        # Scene 3: Good night
        (
            [("$ good night", ORANGE), ("", WHITE),
             ("😴 Mode malam diaktifkan!", WHITE),
             ("", WHITE),
             ("✅ Bedroom Light   → OFF", GREEN),
             ("✅ Bedroom AC      → 26°C low", GREEN),
             ("✅ Standing Fan    → Speed 1", GREEN),
             ("✅ Front Door      → 🔒 LOCKED", GREEN),
             ("✅ Back Door       → 🔒 LOCKED", GREEN),
             ("", WHITE),
             ("5 devices updated!", GRAY)],
            2.5
        ),
        # Scene 4: Dashboard
        (
            [("$ /dashboard", ORANGE), ("", WHITE),
             ("📊 Smart Home Dashboard", WHITE),
             ("━━━━━━━━━━━━━━━━━━━━━━", GRAY),
             ("Living Room: AC ON 24°C | TV 120W", WHITE),
             ("Bedroom: AC ON 26°C | Fan Speed 1", WHITE),
             ("Kitchen: Fridge 150W | Light ON", WHITE),
             ("Office: PC 350W | Desk Lamp ON", WHITE),
             ("", WHITE),
             ("⚡ Power: 470W | 🔋 12.4 kWh", ORANGE),
             ("📱 Active: 7/18 devices", ORANGE)],
            2.5
        ),
        # Scene 5: Energy
        (
            [("$ /energy", ORANGE), ("", WHITE),
             ("⚡ Power Consumption Report", WHITE),
             ("━━━━━━━━━━━━━━━━━━━━━━", GRAY),
             ("Current draw: 470W", WHITE),
             ("Total energy: 15.6 kWh", WHITE),
             ("", WHITE),
             ("Top consumers:", WHITE),
             ("1. PC Setup     ████████ 350W", ORANGE),
             ("2. Smart Fridge ███     150W", ORANGE),
             ("3. TV Plug      ███     120W", ORANGE),
             ("", WHITE),
             ("💡 Tip: AC using 40% of total power!", GREEN)],
            2.5
        ),
        # Scene 6: GitHub
        (
            [("📦 Project Complete!", ORANGE), ("", WHITE),
             ("🔗 github.com/udinbotak1/", WHITE),
             ("   xiaomi-smarthome-bot", WHITE),
             ("", WHITE),
             ("Features:", WHITE),
             ("✅ 18 IoT devices across 6 rooms", GREEN),
             ("✅ AI voice commands (MiMo)", GREEN),
             ("✅ 5 scene modes", GREEN),
             ("✅ Power monitoring dashboard", GREEN),
             ("✅ Telegram inline controls", GREEN),
             ("", WHITE),
             ("Built for Xiaomi MiMo Application 🚀", ORANGE)],
            3.0
        ),
    ]

    frame_dir = "/tmp/smart_home_frames"
    os.makedirs(frame_dir, exist_ok=True)
    
    frame_num = 0
    for lines, duration in scenes:
        num_frames = int(duration * FPS)
        
        # Typing effect for first few frames
        for f in range(num_frames):
            if f < 10 and lines and lines[0][0].startswith("$ "):
                # Typing animation
                cmd = lines[0][0]
                visible_chars = int(len(cmd) * f / 10)
                display_lines = [(cmd[:visible_chars] + ("█" if f % 2 == 0 else ""), lines[0][1])] + lines[1:]
                img = draw_frame(display_lines)
            else:
                img = draw_frame(lines)
            
            img.save(f"{frame_dir}/frame_{frame_num:05d}.png")
            frame_num += 1

    print(f"Generated {frame_num} frames")
    
    # Compile with ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", f"{frame_dir}/frame_%05d.png",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "28",
        "-vf", f"scale={W}:{H}",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size = os.path.getsize(output_path)
        print(f"✅ Video generated: {output_path} ({size/1024:.0f}KB)")
    else:
        print(f"❌ FFmpeg error: {result.stderr}")
    
    # Cleanup frames
    os.system(f"rm -rf {frame_dir}")

if __name__ == "__main__":
    generate_video()
