import pyautogui
import cv2
import numpy as np
import threading
import customtkinter as ctk
import time
from pynput import keyboard

# Global flags
paused = False
running = True
quit_key = "q"  # Default quit key
pause_key = "p"  # Default pause key

def find_green_circle():
    global running
    while running:
        if paused:
            time.sleep(0.2)
            continue

        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

        lower_green = np.array([40, 100, 100])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

            if len(approx) > 6:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)

                if 10 <= radius <= 100:
                    print(f"Green circle found at {center} with radius {radius}")
                    pyautogui.moveTo(center[0], center[1], duration=0.1)
                    pyautogui.click(center[0], center[1])
                    break


def toggle_pause():
    global paused
    paused = not paused
    if paused:
        status_label.configure(text="Status: Paused", text_color="yellow")
    else:
        status_label.configure(text="Status: Running", text_color="green")

def stop_script():
    global running
    running = False
    status_label.configure(text="Status: Stopped", text_color="red")
    app.destroy()

def on_press(key):
    global quit_key, pause_key
    try:
        if key.char == quit_key:
            stop_script()
        elif key.char == pause_key:
            toggle_pause()
    except AttributeError:
        pass

def set_keys():
    def save_keys():
        global quit_key, pause_key
        quit_key = quit_entry.get()
        pause_key = pause_entry.get()
        key_window.destroy()

    key_window = ctk.CTkToplevel()
    key_window.geometry("300x200")
    key_window.title("Set Keybinds")
    key_window.configure(fg_color="#1e1e1e") 

    quit_label = ctk.CTkLabel(key_window, text="Quit Key:", text_color="white")
    quit_label.pack(pady=5)
    quit_entry = ctk.CTkEntry(key_window)
    quit_entry.insert(0, quit_key)
    quit_entry.pack(pady=5)

    pause_label = ctk.CTkLabel(key_window, text="Pause/Resume Key:", text_color="white")
    pause_label.pack(pady=5)
    pause_entry = ctk.CTkEntry(key_window)
    pause_entry.insert(0, pause_key)
    pause_entry.pack(pady=5)

    save_button = ctk.CTkButton(key_window, text="Save", command=save_keys, corner_radius=10, fg_color="#333333", hover_color="#444444")
    save_button.pack(pady=10)


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.geometry("400x300")
app.title("Business.")
app.resizable(False, False)


frame = ctk.CTkFrame(app, corner_radius=20, fg_color="#1e1e1e")
frame.pack(fill="both", expand=True, padx=15, pady=15)


status_label = ctk.CTkLabel(frame, text="Status: Running", text_color="green", font=("Arial", 16))
status_label.pack(pady=(20, 10)) 


def style_button(button):
    button.bind("<Enter>", lambda e: button.configure(fg_color="#444444", hover_color="#555555"))
    button.bind("<Leave>", lambda e: button.configure(fg_color="#333333", hover_color="#444444"))
    button.configure(fg_color="#333333", hover_color="#444444", corner_radius=12, height=45, width=170)

pause_resume_button = ctk.CTkButton(frame, text="Pause/Resume", command=toggle_pause)
style_button(pause_resume_button)
pause_resume_button.pack(pady=10)

stop_button = ctk.CTkButton(frame, text="Stop", command=stop_script)
style_button(stop_button)
stop_button.pack(pady=10)

keybind_button = ctk.CTkButton(frame, text="Set Keybinds", command=set_keys)
style_button(keybind_button)
keybind_button.pack(pady=10)


green_circle_thread = threading.Thread(target=find_green_circle, daemon=True)
green_circle_thread.start()

listener = keyboard.Listener(on_press=on_press)
listener.start()


def on_closing():
    global running
    running = False
    listener.stop() 
    app.destroy()

app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()