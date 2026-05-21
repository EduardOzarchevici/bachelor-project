# import os
#
# os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
#
# import customtkinter as ctk
# import keyboard
# from ui.lock_screen import LockScreen
#
# # Set global appearance
# ctk.set_appearance_mode("Dark")
# ctk.set_default_color_theme("blue")
#
#
# class ProductivityApp(ctk.CTk):
#     def __init__(self):
#         super().__init__()
#         self.title("Productivity & Fitness Tracker")
#         self.geometry("500x350")
#
#         # Main UI Elements
#         self.title_label = ctk.CTkLabel(self, text="Control Panel", font=("Arial", 24, "bold"))
#         self.title_label.pack(pady=30)
#
#         self.info_label = ctk.CTkLabel(
#             self,
#             text="When time expires, the screen will lock.\nEmergency Kill Switch: ALT + 0 + L",
#             font=("Arial", 14)
#         )
#         self.info_label.pack(pady=10)
#
#         # Trigger Button
#         self.btn_trigger = ctk.CTkButton(
#             self,
#             text="Test Penalty Lock Screen",
#             width=250,
#             height=50,
#             font=("Arial", 16),
#             command=self.trigger_penalty
#         )
#         self.btn_trigger.pack(pady=40)
#
#         # Register the global kill switch hotkey
#         keyboard.add_hotkey('alt+0+l', self.handle_kill_switch_event)
#
#         self.lock_screen_window = None
#
#     def trigger_penalty(self):
#         """ Spawns the lock screen if it doesn't already exist. """
#         if self.lock_screen_window is None or not self.lock_screen_window.winfo_exists():
#             print("Penalty triggered! Locking screen...")
#             self.lock_screen_window = LockScreen(
#                 self,
#                 target_pushups=5,
#                 on_unlock_callback=self.on_penalty_cleared
#             )
#
#     def on_penalty_cleared(self):
#         print("Workout completed! Screen unlocked.")
#
#     def handle_kill_switch_event(self):
#         """ Triggered by the keyboard module (Background Thread). """
#         print("KILL SWITCH DETECTED! Routing command to main UI thread...")
#         self.after(0, self.force_close_lock_screen)
#
#     def force_close_lock_screen(self):
#         """ Executes the actual destruction of the lock screen (Main Thread). """
#         if self.lock_screen_window and self.lock_screen_window.winfo_exists():
#             print("Safely destroying lock screen resources...")
#             self.lock_screen_window.release_resources()
#             self.lock_screen_window.destroy()
#             print("Lock screen destroyed.")
#
#
# if __name__ == "__main__":
#     app = ProductivityApp()
#     app.mainloop()

import os
import sys

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import customtkinter as ctk
from ui.main_window import MainWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()