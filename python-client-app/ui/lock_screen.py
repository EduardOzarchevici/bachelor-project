import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from vision.pose_detector import PushupCounter
from ui.theme import COLORS, FONTS, SPACING


class LockScreen(ctk.CTkToplevel):
    def __init__(self, master, target_pushups=5, on_unlock_callback=None):
        super().__init__(master)
        self.target_pushups = target_pushups
        self.on_unlock_callback = on_unlock_callback
        self._current_count = 0

        self.configure(fg_color=COLORS["bg"])

        self.container = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=SPACING["card_radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.container.pack(fill="both", expand=True, padx=48, pady=48)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.grid(row=0, column=0, padx=32, pady=(32, 16), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="SESSION LOCKED",
            font=ctk.CTkFont(family=FONTS["small"][0], size=11, weight="bold"),
            text_color=COLORS["danger"],
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Complete your pushups to unlock",
            font=ctk.CTkFont(family=FONTS["title"][0], size=28, weight="bold"),
            text_color=COLORS["text"],
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        ctk.CTkLabel(
            header,
            text="Position yourself in frame. The camera will count each rep automatically.",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            text_color=COLORS["text_muted"],
            wraplength=700,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

        stats_row = ctk.CTkFrame(self.container, fg_color="transparent")
        stats_row.grid(row=1, column=0, padx=32, pady=(0, 16), sticky="ew")
        stats_row.grid_columnconfigure((0, 1), weight=1)

        counter_card = ctk.CTkFrame(
            stats_row,
            fg_color=COLORS["bg"],
            corner_radius=SPACING["card_radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        counter_card.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkLabel(
            counter_card,
            text="Progress",
            font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
            text_color=COLORS["text_muted"],
        ).pack(anchor="w", padx=20, pady=(16, 4))

        self.counter_label = ctk.CTkLabel(
            counter_card,
            text=f"0 / {self.target_pushups}",
            font=ctk.CTkFont(family=FONTS["stat_value"][0], size=36, weight="bold"),
            text_color=COLORS["accent"],
        )
        self.counter_label.pack(anchor="w", padx=20)

        self.progress_bar = ctk.CTkProgressBar(
            counter_card,
            height=10,
            progress_color=COLORS["accent"],
            fg_color=COLORS["border"],
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(12, 20))
        self.progress_bar.set(0)

        hint_card = ctk.CTkFrame(
            stats_row,
            fg_color=COLORS["accent_soft"],
            corner_radius=SPACING["card_radius"],
            border_width=1,
            border_color=COLORS["border"],
        )
        hint_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(
            hint_card,
            text="Tips",
            font=ctk.CTkFont(family=FONTS["subheading"][0], size=FONTS["subheading"][1], weight="bold"),
            text_color=COLORS["accent"],
        ).pack(anchor="w", padx=20, pady=(16, 8))

        for tip in (
            "Keep your whole body visible",
            "Go down until arms bend ~90°",
            "Emergency unlock: Alt + 0 + L",
        ):
            ctk.CTkLabel(
                hint_card,
                text=f"• {tip}",
                font=ctk.CTkFont(family=FONTS["small"][0], size=FONTS["small"][1]),
                text_color=COLORS["text"],
                justify="left",
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(hint_card, text="").pack(pady=8)

        video_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["bg"],
            corner_radius=SPACING["card_radius"],
            border_width=2,
            border_color=COLORS["border"],
        )
        video_frame.grid(row=2, column=0, padx=32, pady=(0, 32), sticky="nsew")
        video_frame.grid_rowconfigure(0, weight=1)
        video_frame.grid_columnconfigure(0, weight=1)

        self.video_label = ctk.CTkLabel(
            video_frame,
            text="Initializing camera…",
            font=ctk.CTkFont(family=FONTS["body"][0], size=FONTS["body"][1]),
            text_color=COLORS["text_muted"],
            fg_color=COLORS["bg"],
        )
        self.video_label.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

        self.update()
        self.after(200, self.enforce_fullscreen)

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.pushup_counter = PushupCounter()

        if not self.cap.isOpened():
            self.video_label.configure(
                text="Camera unavailable — check your webcam connection.",
                text_color=COLORS["danger"],
            )
            return

        self.update_video_feed()

    def enforce_fullscreen(self):
        self.state("zoomed")
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.disable_close_event)
        self.focus_force()
        self.grab_set()

    def disable_close_event(self):
        pass

    def _update_progress(self, current_count):
        self._current_count = current_count
        self.counter_label.configure(text=f"{current_count} / {self.target_pushups}")
        progress = min(1.0, current_count / self.target_pushups) if self.target_pushups else 0
        self.progress_bar.set(progress)

    def update_video_feed(self) -> None:
        success, frame = self.cap.read()

        if success:
            frame = cv2.flip(frame, 1)
            processed_frame, current_count = self.pushup_counter.process_frame(frame)
            self._update_progress(current_count)

            if current_count >= self.target_pushups:
                self.unlock_system()
                return

            color_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(color_frame)
            pil_img = pil_img.resize((960, 540), Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(image=pil_img)

            self.video_label.configure(image=photo_image, text="")
            self.video_label.image = photo_image
        else:
            self.video_label.configure(
                text="Failed to read camera frame.",
                text_color=COLORS["danger"],
            )

        self.after(15, self.update_video_feed)

    def release_resources(self):
        if self.cap.isOpened():
            self.cap.release()

    def unlock_system(self):
        self.release_resources()
        if self.on_unlock_callback:
            self.on_unlock_callback()
        self.destroy()
