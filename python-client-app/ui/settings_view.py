import threading
import customtkinter as ctk

from core.api_client import ApiClient
from ui.theme import COLORS, FONTS, SPACING


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, on_pushups_saved=None):
        super().__init__(master, fg_color=COLORS["bg"])
        self.api = ApiClient()
        self.on_pushups_saved = on_pushups_saved

        self.pushups_target_var = ctk.IntVar(value=5)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING["page_padx"], pady=(SPACING["page_pady"], 8))

        ctk.CTkLabel(
            header,
            text="Settings",
            font=ctk.CTkFont(family=FONTS["title"][0], size=FONTS["title"][1], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Penalty workout configuration",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(6, 0))

        card = ctk.CTkFrame(
            self,
            corner_radius=SPACING["card_radius"],
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        card.pack(fill="x", padx=SPACING["page_padx"], pady=(8, SPACING["page_pady"]))

        ctk.CTkLabel(
            card,
            text="Pushups per penalty session",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=FONTS["subheading"][1], weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20, pady=(20, 8))

        self.value_label = ctk.CTkLabel(
            card,
            text="5",
            font=ctk.CTkFont(family=FONTS["stat_value"][0], size=28, weight="bold"),
            text_color=COLORS["accent"],
        )
        self.value_label.pack(anchor="w", padx=20)

        self.slider = ctk.CTkSlider(
            card,
            from_=1,
            to=50,
            number_of_steps=49,
            command=self._on_slider_changed,
        )
        self.slider.pack(fill="x", padx=20, pady=(10, 6))
        self.slider.set(5)

        slider_hint = ctk.CTkLabel(
            card,
            text="This value is saved on the backend and used when the penalty lock screen appears.",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
            wraplength=820,
            justify="left",
        )
        slider_hint.pack(anchor="w", padx=20, pady=(0, 18))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))
        btn_row.grid_columnconfigure(0, weight=1)

        self.save_btn = ctk.CTkButton(
            btn_row,
            text="Save",
            height=40,
            width=140,
            font=ctk.CTkFont(family=FONTS["body_bold"][0], size=FONTS["body_bold"][1], weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.save,
        )
        self.save_btn.pack(side="right")

        self.status_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 14))

    def set_pushups_target(self, value: int):
        if value < 1:
            value = 1
        if value > 50:
            value = 50
        self.pushups_target_var.set(value)
        self.slider.set(value)
        self.value_label.configure(text=str(value))

    def _on_slider_changed(self, _val):
        val = int(round(self.slider.get()))
        self.pushups_target_var.set(val)
        self.value_label.configure(text=str(val))

    def save(self):
        target = int(self.pushups_target_var.get())
        self.save_btn.configure(state="disabled", text="Saving...")
        self.status_label.configure(text="Updating backend...", text_color=COLORS["text_muted"])
        threading.Thread(target=self._async_save, args=(target,), daemon=True).start()

    def _async_save(self, target: int):
        try:
            resp = self.api.put("/settings/pushups", json={"pushupsTarget": target}, timeout=5)
            if resp.status_code == 200:
                self.after(0, self._save_success, target)
            else:
                self.after(0, self._save_failed)
        except Exception:
            self.after(0, self._save_failed)

    def _save_success(self, target: int):
        self.save_btn.configure(state="normal", text="Save")
        self.set_pushups_target(target)
        self.status_label.configure(text="Saved.", text_color=COLORS["accent"])
        if self.on_pushups_saved:
            self.on_pushups_saved(target)

    def _save_failed(self):
        self.save_btn.configure(state="normal", text="Save")
        self.status_label.configure(text="Save failed (server offline?).", text_color=COLORS["danger"])

