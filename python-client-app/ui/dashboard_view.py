import threading
import requests
import customtkinter as ctk
from core.api_client import ApiClient
from ui.theme import COLORS, FONTS, SPACING


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_open_pomodoro=None, on_open_habits=None):
        super().__init__(master, fg_color=COLORS["bg"])

        self.api = ApiClient()
        self.on_open_pomodoro = on_open_pomodoro
        self.on_open_habits = on_open_habits
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=SPACING["page_padx"], pady=(SPACING["page_pady"], 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(family=FONTS["title"][0], size=FONTS["title"][1], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Your progress at a glance",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.refresh_btn = ctk.CTkButton(
            header,
            text="Refresh",
            width=100,
            height=34,
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            fg_color=COLORS["card"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self.fetch_dashboard_data,
        )
        self.refresh_btn.grid(row=0, column=1, rowspan=2, padx=(16, 0))

        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.grid(row=1, column=0, padx=SPACING["page_padx"], pady=(8, 16), sticky="ew")
        stats_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.xp_var = ctk.StringVar(value="—")
        self.tasks_var = ctk.StringVar(value="—")
        self.pushups_var = ctk.StringVar(value="0")
        self.xp_sub_var = ctk.StringVar(value="Loading...")
        self.tasks_sub_var = ctk.StringVar(value="Loading...")
        self.pushups_sub_var = ctk.StringVar(value="Penalty workouts")

        self.create_stat_card(stats_row, 0, "XP", self.xp_var, self.xp_sub_var, COLORS["accent"])
        self.create_stat_card(stats_row, 1, "Active Habits", self.tasks_var, self.tasks_sub_var, COLORS["today"])
        self.create_stat_card(stats_row, 2, "Pushups Done", self.pushups_var, self.pushups_sub_var, COLORS["warning"])

        actions_card = ctk.CTkFrame(
            self,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        actions_card.grid(row=2, column=0, padx=SPACING["page_padx"], pady=(0, SPACING["page_pady"]), sticky="new")
        actions_card.grid_columnconfigure((0, 1), weight=1)

        actions_header = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_header.grid(row=0, column=0, columnspan=2, padx=24, pady=(20, 16), sticky="ew")

        ctk.CTkLabel(
            actions_header,
            text="Quick Actions",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=FONTS["subheading"][1], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            actions_header,
            text="Start a focused work session or review your habit tracker.",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(6, 0))

        buttons_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        buttons_row.grid(row=1, column=0, columnspan=2, padx=24, pady=(0, 24), sticky="ew")
        buttons_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            buttons_row,
            text="Open Pomodoro Timer",
            height=52,
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.on_open_pomodoro,
        ).grid(row=0, column=0, padx=(0, 12), sticky="ew")

        ctk.CTkButton(
            buttons_row,
            text="View Habit Spreadsheet",
            height=52,
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            fg_color=COLORS["card_hover"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self.on_open_habits,
        ).grid(row=0, column=1, padx=(12, 0), sticky="ew")

        self.fetch_dashboard_data()

    def create_stat_card(self, parent, column, title, value_var, sub_var, accent):
        card = ctk.CTkFrame(
            parent,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0 if column == 2 else 8), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        accent_bar = ctk.CTkFrame(card, height=4, corner_radius=0, fg_color=accent)
        accent_bar.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, padx=20, pady=(18, 4), sticky="w")

        ctk.CTkLabel(
            card,
            textvariable=value_var,
            font=ctk.CTkFont(family=FONTS["stat_value"][0], size=28, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=2, column=0, padx=20, sticky="w")

        ctk.CTkLabel(
            card,
            textvariable=sub_var,
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=accent,
        ).grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

    def fetch_dashboard_data(self):
        self.xp_var.set("—")
        self.tasks_var.set("—")
        self.xp_sub_var.set("Loading...")
        self.tasks_sub_var.set("Loading...")
        threading.Thread(target=self._async_fetch_data, daemon=True).start()

    def _async_fetch_data(self):
        try:
            stats_response = self.api.get("/stats", timeout=5)
            tasks_response = self.api.get("/tasks", timeout=5)

            if stats_response.status_code == 200 and tasks_response.status_code == 200:
                stats_data = stats_response.json()
                tasks_data = tasks_response.json()
                xp = stats_data.get("xp", 0)
                task_count = len(tasks_data)
                self.after(0, self._update_ui, xp, task_count)
            else:
                self.after(0, self._update_ui_error)
        except requests.RequestException:
            self.after(0, self._update_ui_error)

    def _update_ui(self, xp, task_count):
        self.xp_var.set(str(xp))
        self.tasks_var.set(str(task_count))
        self.xp_sub_var.set("Total completed tasks")
        self.tasks_sub_var.set("Tracked in spreadsheet")

    def _update_ui_error(self):
        self.xp_var.set("Offline")
        self.tasks_var.set("—")
        self.xp_sub_var.set("Could not reach server")
        self.tasks_sub_var.set("Check API connection")
