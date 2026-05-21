import threading
import customtkinter as ctk
from core.api_client import ApiClient
from ui.theme import COLORS, FONTS, SPACING


class AuthView(ctk.CTkFrame):
    def __init__(self, master, on_auth_success):
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_auth_success = on_auth_success
        self.api = ApiClient()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.grid(row=0, column=0)
        wrapper.grid_columnconfigure((0, 1), weight=1)

        brand_panel = ctk.CTkFrame(
            wrapper,
            width=420,
            height=480,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["accent_soft"],
            border_width=1,
            border_color=COLORS["border"],
        )
        brand_panel.grid(row=0, column=0, padx=(0, 16), sticky="nsew")
        brand_panel.grid_propagate(False)

        ctk.CTkLabel(
            brand_panel,
            text="FitBlocker",
            font=ctk.CTkFont(family=FONTS["title"][0], size=34, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w", padx=40, pady=(48, 12))

        ctk.CTkLabel(
            brand_panel,
            text="Build discipline through\nhabits, focus sessions,\nand fitness accountability.",
            font=ctk.CTkFont(family=FONTS["body"][0], size=15),
            text_color=COLORS["text_muted"],
            justify="left",
        ).pack(anchor="w", padx=40)

        for bullet in (
            "Track daily habits over 3 months",
            "Earn XP as you complete tasks",
            "Pomodoro with penalty lock screen",
        ):
            ctk.CTkLabel(
                brand_panel,
                text=f"  •  {bullet}",
                font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
                text_color=COLORS["text"],
                justify="left",
            ).pack(anchor="w", padx=40, pady=(14, 0))

        self.container = ctk.CTkFrame(
            wrapper,
            width=400,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.container.grid(row=0, column=1, padx=(16, 0))
        self.container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.container,
            text="Sign in",
            font=ctk.CTkFont(family=FONTS["heading"][0], size=FONTS["heading"][1], weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=0, column=0, pady=(36, 6), padx=36)

        ctk.CTkLabel(
            self.container,
            text="Access your productivity workspace",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, pady=(0, 24), padx=36)

        self.username_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Username",
            width=300,
            height=42,
            border_color=COLORS["border"],
            fg_color=COLORS["bg"],
        )
        self.username_entry.grid(row=2, column=0, pady=8, padx=36)

        self.password_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Password",
            show="*",
            width=300,
            height=42,
            border_color=COLORS["border"],
            fg_color=COLORS["bg"],
        )
        self.password_entry.grid(row=3, column=0, pady=8, padx=36)

        self.btn_login = ctk.CTkButton(
            self.container,
            text="Sign In",
            width=300,
            height=42,
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.attempt_login,
        )
        self.btn_login.grid(row=4, column=0, pady=(18, 8), padx=36)

        self.btn_register = ctk.CTkButton(
            self.container,
            text="Create Account",
            width=300,
            height=42,
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            hover_color=COLORS["card_hover"],
            command=self.attempt_register,
        )
        self.btn_register.grid(row=5, column=0, pady=8, padx=36)

        self.status_label = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["danger"],
        )
        self.status_label.grid(row=6, column=0, pady=(8, 32), padx=36)

        self.username_entry.bind("<Return>", lambda _: self.attempt_login())
        self.password_entry.bind("<Return>", lambda _: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.configure(text="Please fill in all fields", text_color=COLORS["danger"])
            return
        self.status_label.configure(text="Authenticating...", text_color=COLORS["text_muted"])
        threading.Thread(target=self._async_login, args=(username, password), daemon=True).start()

    def _async_login(self, username, password):
        try:
            response = self.api.post("/auth/login", json={"username": username, "password": password}, timeout=5)
            if response.status_code == 200:
                token = response.json().get("token")
                self.api.set_token(token)
                self.after(0, self.on_auth_success)
            else:
                self.after(0, lambda: self.status_label.configure(text="Invalid credentials", text_color=COLORS["danger"]))
        except Exception:
            self.after(0, lambda: self.status_label.configure(text="Cannot reach server", text_color=COLORS["danger"]))

    def attempt_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            self.status_label.configure(text="Please fill in all fields", text_color=COLORS["danger"])
            return
        self.status_label.configure(text="Creating account...", text_color=COLORS["text_muted"])
        threading.Thread(target=self._async_register, args=(username, password), daemon=True).start()

    def _async_register(self, username, password):
        try:
            response = self.api.post("/auth/register", json={"username": username, "password": password}, timeout=5)
            if response.status_code == 200:
                self.after(
                    0,
                    lambda: self.status_label.configure(
                        text="Account created — you can sign in now.",
                        text_color=COLORS["accent"],
                    ),
                )
            else:
                self.after(0, lambda: self.status_label.configure(text="Username already taken", text_color=COLORS["danger"]))
        except Exception:
            self.after(0, lambda: self.status_label.configure(text="Cannot reach server", text_color=COLORS["danger"]))
