#!/usr/bin/env python3
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from st7789_hw import ST7789_HW

# =========================
# KEY SETTINGS
# -> please modify this to match your system
# =========================

# Insert your own API-Key here
API_KEY = "abcdefghiklmnopqrstuvwxyz1234567890"

# Since the Script is running on the same device,
# this should be correct. Change only if necessary!
OCTO_JOBURL = "http://127.0.0.1/api/job"
OCTO_PRINTERURL = "http://127.0.0.1/api/printer",

#Display background image:
#insert the path to your image file!
BACKGROUND_PATH = "/home/admin/octodisplay/background.png"

# =========================
# END OF KEY SETTINGS
# =========================

HEADERS = {
    "X-Api-Key": API_KEY
}

# ==================================

# =========================
# DISPLAY CONFIG
# =========================
#use rotation=270 when having the cables on the right side
#use rotation=90  when having the cables on the left side
#this is specific for the aliexpress display, adjust if you
#use different hardware. 

display = ST7789_HW(
    width=320,
    height=240,
    dc=24,
    rst=25,
    x_offset=0,
    y_offset=0,
    rotation=270
)

display.init()

WIDTH = 320
HEIGHT = 240

# =========================
# LOAD BACKGROUND
# =========================
background = Image.open(BACKGROUND_PATH).convert("RGB")
background = background.resize((WIDTH, HEIGHT))

# =========================
# FONTS
# =========================
font_big = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    24
)

font_medium = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    20
)

font_small = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    16
)

# =========================
# TEXT POSITIONS
# =========================
# you can adjust these if your image looks different

# Extruder
POS_EXTRUDER = (25, 60)

# Bed
POS_BED = (97, 60)

# Estimated total time
POS_ESTIMATED = (165, 65)

# Remaining time
POS_TIME = (243, 65)

# Filename
POS_FILENAME = (70, 125)

# Progress text
POS_PROGRESS_TEXT = (125, 200)

# Progress bar
BAR_X = 20
BAR_Y = 200
BAR_W = 280
BAR_H = 25


# =========================
# FUNCTIONS
# =========================

def normalize_value(v):
    if v is False or v == "false" or v is None:
        return 0
    return v

def format_time(seconds):

    if seconds is None:
        return "--:--"

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60

    return f"{h:02}:{m:02}"


def get_printer_data():

    try:
        r = requests.get(
            OCTO_JOBURL,
            headers=HEADERS,
            timeout=5
        )

        job = r.json()

        # Temperatures
        r2 = requests.get(
            OCTO_PRINTERURL,
            headers=HEADERS,
            timeout=5
        )

        printer = r2.json()

        tool_temp = printer["temperature"]["tool0"]["actual"]
        bed_temp = printer["temperature"]["bed"]["actual"]

        # Printing active?
        printactive = 0

        try:
            printactive = printer["state"]["flags"]["printing"]
        except:
            pass

        # Print progress
        progress = job["progress"]["completion"]

        if progress is None:
            progress = 0

        # Remaining time
        time_left = job["progress"]["printTimeLeft"]

        # Estimated total time
        time_estimated = job["job"]["estimatedPrintTime"]

        # Filename
        filename = job["job"]["file"]["name"]

        return {
            "tool": round(tool_temp),
            "bed": round(bed_temp),
            "printing": printactive,
            "progress": progress,
            "time_left": time_left,
            "time_estimated": time_estimated,
            "filename": filename
        }

    except Exception as e:

        return {
            "tool": 0,
            "bed": 0,
            "printing": 0,
            "progress": 0,
            "time_left": None,
            "time_estimated": None,
            "filename": "No connection"
        }


# =========================
# MAIN LOOP
# =========================
while True:

    data = get_printer_data()
    image = background.copy()
    draw = ImageDraw.Draw(image)

    # =====================
    # Temperatures
    # =====================
    draw.text(
        POS_EXTRUDER,
        f"{data['tool']}°",
        font=font_big,
        fill=(0, 0, 0)
    )

    draw.text(
        POS_BED,
        f"{data['bed']}°",
        font=font_big,
        fill=(0, 0, 0)
    )

    # =====================
    # Estimated time
    # =====================
    draw.text(
        POS_ESTIMATED,
        format_time(data['time_estimated']),
        font=font_small,
        fill=(0, 0, 0)
    )

    # =====================
    # Remaining time
    # =====================
    draw.text(
        POS_TIME,
        format_time(data['time_left']),
        font=font_small,
        fill=(0, 0, 0)
    )

    # =====================
    # File name
    # =====================
    filename = data.get("filename") or "No print active"

    if len(filename) > 24:
        filename = filename[:24] + "..."

    draw.text(
        POS_FILENAME,
        filename,
        font=font_small,
        fill=(255, 255, 255)
    )

    # =====================
    # Progress bar
    # =====================
    progress = int(data["progress"])

    # Frame
    draw.rectangle(
        (BAR_X, BAR_Y, BAR_X + BAR_W, BAR_Y + BAR_H),
        outline=(255, 255, 255),
        width=2
    )

    # Filling
    fill_w = int((progress / 100) * (BAR_W - 4))

    draw.rectangle(
        (
            BAR_X + 2,
            BAR_Y + 2,
            BAR_X + 2 + fill_w,
            BAR_Y + BAR_H - 2
        ),
        fill=(255, 255, 255)
    )

    # Percentage text
    draw.text(
        POS_PROGRESS_TEXT,
        f"{progress}%",
        font=font_medium,
        fill=(0, 0, 0)
    )

    # Refresh display
    display.image(image)

    # Refresh every X seconds (default = 2)
    time.sleep(2)
