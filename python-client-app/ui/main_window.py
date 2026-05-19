import customtkinter as ctk
import keyboard
from ui.lock_screen import LockScreen
from ui.dashboard_view import DashboardView
from ui.pomodoro_view import PomodoroView
from ui.todo_tracker_view import TodoTrackerView


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Productivity & Fitness Tracker")
        self.geometry("1000x650")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="FitBlocker", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_todo = ctk.CTkButton(self.sidebar_frame, text="Habits/Tasks", command=self.show_todo_tracker)
        self.btn_todo.grid(row=2, column=0, padx=20, pady=10)

        self.btn_pomodoro = ctk.CTkButton(self.sidebar_frame, text="Pomodoro", command=self.show_pomodoro)
        self.btn_pomodoro.grid(row=3, column=0, padx=20, pady=10)

        self.btn_trigger = ctk.CTkButton(self.sidebar_frame, text="Test Penalty", fg_color="red", hover_color="darkred",
                                         command=self.trigger_penalty)
        self.btn_trigger.grid(row=5, column=0, padx=20, pady=(10, 20))

        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_view = DashboardView(self.main_content_frame)
        self.pomodoro_view = PomodoroView(self.main_content_frame, penalty_callback=self.trigger_penalty)
        self.todo_tracker_view = TodoTrackerView(self.main_content_frame)

        keyboard.add_hotkey('alt+0+l', self.handle_kill_switch_event)
        self.lock_screen_window = None

        self.show_todo_tracker()

    def show_dashboard(self):
        self.pomodoro_view.grid_forget()
        self.todo_tracker_view.grid_forget()
        self.dashboard_view.grid(row=0, column=0, sticky="nsew")

    def show_pomodoro(self):
        self.dashboard_view.grid_forget()
        self.todo_tracker_view.grid_forget()
        self.pomodoro_view.grid(row=0, column=0, sticky="nsew")

    def show_todo_tracker(self):
        self.dashboard_view.grid_forget()
        self.pomodoro_view.grid_forget()
        self.todo_tracker_view.grid(row=0, column=0, sticky="nsew")

    def trigger_penalty(self):
        if self.lock_screen_window is None or not self.lock_screen_window.winfo_exists():
            self.lock_screen_window = LockScreen(
                self,
                target_pushups=5,
                on_unlock_callback=self.on_penalty_cleared
            )

    def on_penalty_cleared(self):
        pass

    def handle_kill_switch_event(self):
        self.after(0, self.force_close_lock_screen)

    def force_close_lock_screen(self):
        if self.lock_screen_window and self.lock_screen_window.winfo_exists():
            self.lock_screen_window.release_resources()
            self.lock_screen_window.destroy()