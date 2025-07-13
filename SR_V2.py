import cv2
import numpy as np
import pyautogui
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
from PIL import Image, ImageTk, ImageDraw
import time
import sys
import pystray
from pystray import MenuItem as item


class ScreenRecorder:
    def __init__(self, fps=15):
        self.is_recording = False
        self.fps = fps
        self.out = None

    def start(self, output_path):
        self.is_recording = True
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.out = cv2.VideoWriter(output_path, fourcc, self.fps, screen_size)

        colors = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 255, 0)]

        while self.is_recording:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Rainbow cursor
            x, y = pyautogui.position()
            color = colors[int(time.time() * 2) % len(colors)]
            cv2.circle(frame, (x, y), 20, color, 3)

            self.out.write(frame)
            time.sleep(1 / self.fps)

        self.out.release()

    def stop(self):
        self.is_recording = False


recorder = ScreenRecorder()
icon = None  # pystray icon reference

def start_recording():
    folder = filedialog.askdirectory(title="Select Save Folder")
    if not folder:
        return

    output_file = f"{folder}/screen_recording.avi"
    status_label.config(text="Recording...")
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")

    t = threading.Thread(target=recorder.start, args=(output_file,))
    t.start()

def stop_recording():
    recorder.stop()
    status_label.config(text="Stopped")
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    messagebox.showinfo("Done", "Recording saved.")
    if icon:
        icon.stop()
    root.deiconify()

def animate_text():
    text = "   Welcome to Custom Screen Recorder..."
    x = 500
    while True:
        if not root.winfo_exists():
            break
        banner_label.config(text=text)
        banner_label.place(x=x, y=5)
        x -= 2
        if x < -len(text) * 10:
            x = 500
        time.sleep(0.05)

def create_image():
    # Make a simple tray icon image
    img = Image.new('RGB', (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 64, 64], fill="black")
    d.ellipse([16, 16, 48, 48], fill="green")
    return img

def on_minimize(event):
    if root.state() == 'iconic':
        root.withdraw()
        show_tray_icon()

def show_tray_icon():
    global icon
    menu = (
        item('Stop Recording', lambda: stop_recording()),
        item('Exit', on_exit)
    )
    icon = pystray.Icon("CustomScreenRecorder", create_image(), "Screen Recorder", menu)
    icon.run()

def on_exit():
    if recorder.is_recording:
        recorder.stop()
    icon.stop()
    root.destroy()
    sys.exit()

# ---- GUI ----
root = ThemedTk(theme="arc")
root.configure(bg="black")
root.title("🎥 Custom Screen Recorder")
root.geometry("500x250")
root.resizable(False, False)

root.bind("<Unmap>", on_minimize)

panel = tk.Frame(root, bg="black")
panel.pack(fill="both", expand=True)

banner_label = tk.Label(panel, text="", font=("Helvetica", 12, "bold"), fg="cyan", bg="black")
banner_label.place(x=500, y=5)

title = tk.Label(panel, text="Custom Screen Recorder", font=("Helvetica", 18, "bold"), fg="green", bg="black")
title.pack(pady=40)

controls = ttk.Frame(panel)
controls.pack(pady=20)

start_btn = ttk.Button(controls, text="▶️ Start", command=start_recording)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = ttk.Button(controls, text="⏹️ Stop", command=stop_recording, state="disabled")
stop_btn.grid(row=0, column=1, padx=10)

status_label = tk.Label(panel, text="Idle", font=("Helvetica", 12), fg="blue", bg="black")
status_label.pack(pady=10)

threading.Thread(target=animate_text, daemon=True).start()

root.mainloop()
