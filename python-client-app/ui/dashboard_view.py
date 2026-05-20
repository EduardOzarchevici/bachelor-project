import threading
import requests
import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.api_base_url = "http://localhost:8081/api"

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.header_label = ctk.CTkLabel(self, text="Welcome Back!", font=ctk.CTkFont(size=28, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 30), sticky="w")

        self.level_xp_var = ctk.StringVar(value="Loading...")
        self.tasks_var = ctk.StringVar(value="Loading...")
        self.pushups_var = ctk.StringVar(value="0")

        self.stats_frame_1 = self.create_stat_card("Level / XP", self.level_xp_var)
        self.stats_frame_1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.stats_frame_2 = self.create_stat_card("Total Habits/Tasks", self.tasks_var)
        self.stats_frame_2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.stats_frame_3 = self.create_stat_card("Total Pushups", self.pushups_var)
        self.stats_frame_3.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(20, 10), sticky="nsew")
        self.action_frame.grid_rowconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure((0, 1), weight=1)

        self.quick_pomodoro_btn = ctk.CTkButton(self.action_frame, text="Start 25m Pomodoro", height=60,
                                                font=ctk.CTkFont(size=16))
        self.quick_pomodoro_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.refresh_btn = ctk.CTkButton(self.action_frame, text="Refresh Dashboard", height=60,
                                         font=ctk.CTkFont(size=16), command=self.fetch_dashboard_data)
        self.refresh_btn.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        self.fetch_dashboard_data()

    def create_stat_card(self, title, string_var):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid_rowconfigure((0, 1), weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14))
        title_label.grid(row=0, column=0, pady=(20, 5))

        value_label = ctk.CTkLabel(frame, textvariable=string_var, font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="#00cc66")
        value_label.grid(row=1, column=0, pady=(0, 20))

        return frame

    def fetch_dashboard_data(self):
        self.level_xp_var.set("Loading...")
        self.tasks_var.set("Loading...")
        threading.Thread(target=self._async_fetch_data, daemon=True).start()

    def _async_fetch_data(self):
        try:
            stats_response = requests.get(f"{self.api_base_url}/stats", timeout=5)
            tasks_response = requests.get(f"{self.api_base_url}/tasks", timeout=5)

            if stats_response.status_code == 200 and tasks_response.status_code == 200:
                stats_data = stats_response.json()
                tasks_data = tasks_response.json()

                level = stats_data.get("level", 1)
                xp = stats_data.get("xp", 0)
                task_count = len(tasks_data)

                self.after(0, self._update_ui, level, xp, task_count)
            else:
                self.after(0, self._update_ui_error)
        except requests.RequestException:
            self.after(0, self._update_ui_error)

    def _update_ui(self, level, xp, task_count):
        self.level_xp_var.set(f"Lvl {level} - {xp} XP")
        self.tasks_var.set(f"{task_count} Habits")

    def _update_ui_error(self):
        self.level_xp_var.set("Offline")
        self.tasks_var.set("Offline")