import customtkinter as ctk


class PomodoroView(ctk.CTkFrame):
    def __init__(self, master, penalty_callback):
        super().__init__(master, fg_color="transparent")

        self.penalty_callback = penalty_callback
        self.is_running = False
        self.time_left = 1500
        self.current_mode = "Work"
        self.timer_id = None

        self.grid_rowconfigure((0, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=1, column=0, pady=20)

        self.btn_work = ctk.CTkButton(self.mode_frame, text="Work", command=lambda: self.set_mode("Work"))
        self.btn_work.pack(side="left", padx=10)

        self.btn_short_break = ctk.CTkButton(self.mode_frame, text="Short Break",
                                             command=lambda: self.set_mode("Short Break"))
        self.btn_short_break.pack(side="left", padx=10)

        self.btn_long_break = ctk.CTkButton(self.mode_frame, text="Long Break",
                                            command=lambda: self.set_mode("Long Break"))
        self.btn_long_break.pack(side="left", padx=10)

        self.timer_label = ctk.CTkLabel(self, text="25:00", font=ctk.CTkFont(size=100, weight="bold"))
        self.timer_label.grid(row=2, column=0, pady=20)

        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=3, column=0, pady=20)

        self.btn_start = ctk.CTkButton(self.controls_frame, text="Start", command=self.start_timer)
        self.btn_start.pack(side="left", padx=10)

        self.btn_pause = ctk.CTkButton(self.controls_frame, text="Pause", command=self.pause_timer)
        self.btn_pause.pack(side="left", padx=10)

        self.btn_reset = ctk.CTkButton(self.controls_frame, text="Reset", command=self.reset_timer)
        self.btn_reset.pack(side="left", padx=10)

    def set_mode(self, mode):
        self.pause_timer()
        self.current_mode = mode
        if mode == "Work":
            self.time_left = 1500
        elif mode == "Short Break":
            self.time_left = 300
        elif mode == "Long Break":
            self.time_left = 900
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
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")