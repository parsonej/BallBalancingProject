# wasdctrl2

import tkinter as tk
import servo  # your servo module
import time

xPIN = 18
yPIN = 19
refreshrate = 1./20
anglemag = 10 # [deg] servo set angle (not platform) on button press  
levelangle = 25


class ManualControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Balancing Table Manual Control")
        self.geometry("300x150")

        self.label = tk.Label(self, text="Use WASD to move platform.\nPress ESC to quit.")
        self.label.pack(pady=20)

        self.xset = levelangle
        self.yset = levelangle

        self.pressed_keys = set()

        # Bind key events
        self.bind("<KeyPress>", self.on_key_press)
        self.bind("<KeyRelease>", self.on_key_release)

        # Start servo update loop
        self.update_servo()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in {'w', 'a', 's', 'd'}:
            self.pressed_keys.add(key)
        elif key == 'escape':
            self.cleanup_and_exit()

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def update_servo(self):
        # Calculate xset and yset from pressed keys
        x = 0
        y = 0
        if 'w' in self.pressed_keys:
            y += anglemag*1.25
        if 's' in self.pressed_keys:
            y -= anglemag
        if 'd' in self.pressed_keys:
            x += anglemag*1.25
        if 'a' in self.pressed_keys:
            x -= anglemag

        if (x, y) != (self.xset, self.yset):
            self.xset = x
            self.yset = y
            servo.setx(self.xset + levelangle)
            servo.sety(self.yset + levelangle)
            self.label.config(text=f"xset: {self.xset}, yset: {self.yset}\nPress ESC to quit.")

        # Schedule next update in 50 ms (~20 Hz)
        self.after(50, self.update_servo)

    def cleanup_and_exit(self):
        servo.turnoff()
        print("Exiting manual control.")
        time.sleep(.2)
        self.destroy()


if __name__ == "__main__":
    app = ManualControlApp()
    app.mainloop()
