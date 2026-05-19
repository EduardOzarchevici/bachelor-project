import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.header_label = ctk.CTkLabel(self, text="Welcome Back!", font=ctk.CTkFont(size=28, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 30), sticky="w")

        self.stats_frame_1 = self.create_stat_card("Level / XP", "Lvl 5 - 1200 XP")
        self.stats_frame_1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.stats_frame_2 = self.create_stat_card("Pending Tasks", "4 Tasks")
        self.stats_frame_2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.stats_frame_3 = self.create_stat_card("Total Pushups", "150")
        self.stats_frame_3.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(20, 10), sticky="nsew")
        self.action_frame.grid_rowconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure((0, 1), weight=1)

        self.quick_pomodoro_btn = ctk.CTkButton(self.action_frame, text="Start 25m Pomodoro", height=60,
                                                font=ctk.CTkFont(size=16))
        self.quick_pomodoro_btn.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.quick_task_btn = ctk.CTkButton(self.action_frame, text="Add New Task", height=60,
                                            font=ctk.CTkFont(size=16))
        self.quick_task_btn.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

    def create_stat_card(self, title, value):
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.grid_rowconfigure((0, 1), weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14))
        title_label.grid(row=0, column=0, pady=(20, 5))

        value_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color="#00cc66")
        value_label.grid(row=1, column=0, pady=(0, 20))

        return frame