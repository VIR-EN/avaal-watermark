import os
import shutil
import hashlib
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import tkinter as tk
from tkinter import filedialog, messagebox

# ======================
# CONFIG
# ======================

VISIBLE_OPACITY = 50
LOGO_SCALE = 0.15
PADDING = 40

GHOST_TEXT_ENABLED = True
GHOST_TEXT = "AVAAL INTERNAL"
GHOST_OPACITY = 12
GHOST_SPACING = 400

PROJECT_ID = "AVAAL_INTERNAL_V1"

# ======================
# RESOURCE PATH FIX (Important for PyInstaller)
# ======================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

LOGO_PATH = resource_path("watermark_logo.png")

# ======================
# CORE FUNCTIONS
# ======================

def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def add_watermark(image_path, output_folder, archive_folder):
    base = Image.open(image_path).convert("RGBA")
    width, height = base.size

    # Make overlay larger than image to survive rotation
    diagonal = int((width**2 + height**2) ** 0.5)
    overlay = Image.new("RGBA", (diagonal, diagonal), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("arial.ttf", int(width * 0.25))
    except:
        font = ImageFont.load_default()

    text = "AVAAL"

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    spacing_x = int(text_width * 1.8)
    spacing_y = int(text_height * 2.5)

    # Tile across full diagonal canvas
    for x in range(-diagonal, diagonal * 2, spacing_x):
        for y in range(-diagonal, diagonal * 2, spacing_y):
            draw.text(
                (x, y),
                text,
                fill=(30, 30, 30, 40),  # adjust opacity here
                font=font
            )

    # Rotate after full tiling
    overlay = overlay.rotate(30, expand=True)

    # Center crop back to original image size
    ox, oy = overlay.size
    left = (ox - width) // 2
    top = (oy - height) // 2
    overlay = overlay.crop((left, top, left + width, top + height))

    # Merge
    base = Image.alpha_composite(base, overlay)

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(archive_folder, exist_ok=True)

    output_path = os.path.join(output_folder, os.path.basename(image_path))
    base.convert("RGB").save(output_path, "PNG")

    archive_path = os.path.join(archive_folder, os.path.basename(image_path))
    shutil.move(image_path, archive_path)

def process_images():
    input_folder = filedialog.askdirectory(title="Select Folder With Raw Images")
    if not input_folder:
        return

    output_folder = os.path.join(input_folder, "watermarked_output")
    archive_folder = os.path.join(input_folder, "archived_raw")

    for file in os.listdir(input_folder):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            add_watermark(
                os.path.join(input_folder, file),
                output_folder,
                archive_folder
            )

    messagebox.showinfo("Done", "Images processed successfully!")

# ======================
# UI
# ======================

root = tk.Tk()
root.title("AVAAL Watermark Tool")
root.geometry("360x200")

label = tk.Label(root, text="AVAAL Internal Watermark Tool", font=("Arial", 12))
label.pack(pady=20)

button = tk.Button(
    root,
    text="Select Folder & Process",
    command=process_images,
    height=2,
    width=25
)
button.pack()

root.mainloop()