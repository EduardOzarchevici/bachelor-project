import customtkinter as ctk
import keyboard
from ui.lock_screen import LockScreen
from ui.dashboard_view import DashboardView
from ui.pomodoro_view import PomodoroView
from ui.todo_tracker_view import TodoTrackerView
from ui.auth_view import AuthView
from ui.theme import APP_TITLE, WINDOW_SIZE, MIN_WINDOW_SIZE, COLORS, FONTS, SPACING


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.configure(fg_color=COLORS["bg"])

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.auth_view = AuthView(self, on_auth_success=self.initialize_app_ui)
        self.auth_view.grid(row=0, column=0, sticky="nsew")

        self.sidebar_frame = None
        self.main_content_frame = None
        self.dashboard_view = None
        self.pomodoro_view = None
        self.todo_tracker_view = None
        self.lock_screen_window = None
        self.nav_buttons = {}
        self.active_nav = None

    def initialize_app_ui(self):
        self.auth_view.destroy()
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=SPACING["sidebar_width"],
            corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=0,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.sidebar_frame.grid_propagate(False)

        brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(28, 32), sticky="ew")

        ctk.CTkLabel(
            brand_frame,
            text="FitBlocker",
            font=ctk.CTkFont(family=FONTS["logo"][0], size=FONTS["logo"][1], weight="bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="Focus · Habits · Fitness",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            self.sidebar_frame,
            text="NAVIGATION",
            font=ctk.CTkFont(family=FONTS["small"][0], size=10, weight="bold"),
            text_color=COLORS["text_dim"],
        ).grid(row=1, column=0, padx=24, pady=(0, 8), sticky="w")

        self.nav_buttons["dashboard"] = self._create_nav_button("Dashboard", self.show_dashboard)
        self.nav_buttons["dashboard"].grid(row=2, column=0, padx=16, pady=4, sticky="ew")

        self.nav_buttons["todo"] = self._create_nav_button("Habits & Tasks", self.show_todo_tracker)
        self.nav_buttons["todo"].grid(row=3, column=0, padx=16, pady=4, sticky="ew")

        self.nav_buttons["pomodoro"] = self._create_nav_button("Pomodoro", self.show_pomodoro)
        self.nav_buttons["pomodoro"].grid(row=4, column=0, padx=16, pady=4, sticky="ew")

        footer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer.grid(row=7, column=0, padx=16, pady=(0, 24), sticky="ew")

        ctk.CTkButton(
            footer,
            text="Test Penalty Lock",
            height=36,
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.trigger_penalty,
        ).pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            footer,
            text="Kill switch: Alt + 0 + L",
            font=ctk.CTkFont(family=FONTS["small"][0], size=10),
            text_color=COLORS["text_dim"],
        ).pack()

        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg"])
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_view = DashboardView(
            self.main_content_frame,
            on_open_pomodoro=self.show_pomodoro,
            on_open_habits=self.show_todo_tracker,
        )
        self.pomodoro_view = PomodoroView(self.main_content_frame, penalty_callback=self.trigger_penalty)
        self.todo_tracker_view = TodoTrackerView(self.main_content_frame)

        keyboard.add_hotkey("alt+0+l", self.handle_kill_switch_event)
        self._set_active_nav("dashboard")
        self.show_dashboard()

    def _create_nav_button(self, text, command):
        return ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            height=42,
            anchor="w",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            fg_color="transparent",
            text_color=COLORS["text_muted"],
            hover_color=COLORS["sidebar_hover"],
            command=command,
        )

    def _set_active_nav(self, key):
        self.active_nav = key
        for nav_key, button in self.nav_buttons.items():
            if nav_key == key:
                button.configure(
                    fg_color=COLORS["accent_soft"],
                    text_color=COLORS["accent"],
                    hover_color=COLORS["accent_soft"],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_muted"],
                    hover_color=COLORS["sidebar_hover"],
                )

    def _hide_all_views(self):
        for view in (self.dashboard_view, self.pomodoro_view, self.todo_tracker_view):
            if view is not None:
                view.grid_forget()

    def show_dashboard(self):
        if self.dashboard_view is None:
            return
        self._set_active_nav("dashboard")
        self._hide_all_views()
        self.dashboard_view.grid(row=0, column=0, sticky="nsew")

    def show_pomodoro(self):
        if self.pomodoro_view is None:
            return
        self._set_active_nav("pomodoro")
        self._hide_all_views()
        self.pomodoro_view.grid(row=0, column=0, sticky="nsew")

    def show_todo_tracker(self):
        if self.todo_tracker_view is None:
            return
        self._set_active_nav("todo")
        self._hide_all_views()
        self.todo_tracker_view.grid(row=0, column=0, sticky="nsew")

    def trigger_penalty(self):
        if self.lock_screen_window is None or not self.lock_screen_window.winfo_exists():
            self.lock_screen_window = LockScreen(
                self,
                target_pushups=5,
                on_unlock_callback=self.on_penalty_cleared,
            )

    def on_penalty_cleared(self):
        pass

    def handle_kill_switch_event(self):
        self.after(0, self.force_close_lock_screen)

    def force_close_lock_screen(self):
        if self.lock_screen_window and self.lock_screen_window.winfo_exists():
            self.lock_screen_window.release_resources()
            self.lock_screen_window.destroy()
