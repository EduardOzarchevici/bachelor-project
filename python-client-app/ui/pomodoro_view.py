import customtkinter as ctk
from ui.theme import COLORS, FONTS, SPACING


class PomodoroView(ctk.CTkFrame):
    MODES = {
        "Work": {"seconds": 1500, "color": COLORS["accent"]},
        "Short Break": {"seconds": 300, "color": COLORS["today"]},
        "Long Break": {"seconds": 900, "color": COLORS["warning"]},
    }

    def __init__(self, master, penalty_callback):
        super().__init__(master, fg_color=COLORS["bg"])
        self.penalty_callback = penalty_callback
        self.is_running = False
        self.time_left = self.MODES["Work"]["seconds"]
        self.current_mode = "Work"
        self.timer_id = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            self,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72, relheight=0.78)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="Pomodoro Timer",
            font=ctk.CTkFont(family=FONTS["title"][0], size=FONTS["heading"][1], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, pady=(32, 4))

        ctk.CTkLabel(
            card,
            text="Stay focused — skipping work triggers the penalty lock screen",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, pady=(0, 24))

        self.mode_frame = ctk.CTkFrame(card, fg_color=COLORS["bg"], corner_radius=24)
        self.mode_frame.grid(row=2, column=0, pady=8)

        self.mode_buttons = {}
        for mode in self.MODES:
            btn = ctk.CTkButton(
                self.mode_frame,
                text=mode,
                width=120,
                height=36,
                corner_radius=18,
                font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
                fg_color="transparent",
                text_color=COLORS["text_muted"],
                hover_color=COLORS["card_hover"],
                command=lambda m=mode: self.set_mode(m),
            )
            btn.pack(side="left", padx=4, pady=4)
            self.mode_buttons[mode] = btn

        self.timer_ring = ctk.CTkFrame(card, fg_color=COLORS["bg"], corner_radius=200, width=280, height=280)
        self.timer_ring.grid(row=3, column=0, pady=28)
        self.timer_ring.grid_propagate(False)

        self.timer_label = ctk.CTkLabel(
            self.timer_ring,
            text="25:00",
            font=ctk.CTkFont(family=FONTS["timer"][0], size=FONTS["timer"][1], weight="bold"),
            text_color=COLORS["accent"],
        )
        self.timer_label.place(relx=0.5, rely=0.42, anchor="center")

        self.mode_indicator = ctk.CTkLabel(
            self.timer_ring,
            text="Work Session",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            text_color=COLORS["text_muted"],
        )
        self.mode_indicator.place(relx=0.5, rely=0.62, anchor="center")

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.grid(row=4, column=0, pady=(8, 36))

        self.btn_start = ctk.CTkButton(
            controls,
            text="Start",
            width=110,
            height=44,
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.start_timer,
        )
        self.btn_start.pack(side="left", padx=6)

        self.btn_pause = ctk.CTkButton(
            controls,
            text="Pause",
            width=110,
            height=44,
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            fg_color=COLORS["card_hover"],
            hover_color=COLORS["border"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self.pause_timer,
        )
        self.btn_pause.pack(side="left", padx=6)

        self.btn_reset = ctk.CTkButton(
            controls,
            text="Reset",
            width=110,
            height=44,
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_muted"],
            hover_color=COLORS["card_hover"],
            command=self.reset_timer,
        )
        self.btn_reset.pack(side="left", padx=6)

        self._highlight_mode_button("Work")

    def _highlight_mode_button(self, mode):
        for name, button in self.mode_buttons.items():
            if name == mode:
                button.configure(fg_color=COLORS["accent_soft"], text_color=COLORS["accent"])
            else:
                button.configure(fg_color="transparent", text_color=COLORS["text_muted"])

    def set_mode(self, mode):
        self.pause_timer()
        self.current_mode = mode
        self.time_left = self.MODES[mode]["seconds"]
        self._highlight_mode_button(mode)
        self.update_display()

    def start_timer(self):
        if not self.is_running and self.time_left > 0:
            self.is_running = True
            self.run_timer()

    def pause_timer(self):
        self.is_running = False
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self):
        self.set_mode(self.current_mode)

    def run_timer(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            self.timer_id = self.after(1000, self.run_timer)
        elif self.time_left <= 0:
            self.is_running = False
            self.timer_id = None
            if self.current_mode == "Work":
                self.penalty_callback()

    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        color = self.MODES[self.current_mode]["color"]
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}", text_color=color)
        self.mode_indicator.configure(text=f"{self.current_mode} Session")
