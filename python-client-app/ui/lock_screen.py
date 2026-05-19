import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from vision.pose_detector import PushupCounter


class LockScreen(ctk.CTkToplevel):
    def __init__(self, master, target_pushups=5, on_unlock_callback=None):
        super().__init__(master)
        self.target_pushups = target_pushups
        self.on_unlock_callback = on_unlock_callback

        # 1. Set background color
        self.configure(fg_color="#1a1a1a")

        # 2. Build and pack ALL UI Elements FIRST
        self.title_label = ctk.CTkLabel(
            self,
            text="TIME EXPIRED. DO YOUR PUSHUPS TO UNLOCK.",
            font=("Arial", 30, "bold"),
            text_color="#ff4d4d"
        )
        self.title_label.pack(pady=(40, 10))

        self.counter_label = ctk.CTkLabel(
            self,
            text=f"0 / {self.target_pushups}",
            font=("Arial", 80, "bold"),
            text_color="#00cc66"
        )
        self.counter_label.pack(pady=10)

        self.video_label = ctk.CTkLabel(self, text="Loading camera...")
        self.video_label.pack(expand=True)

        # 3. FORCE Tkinter to draw the UI
        self.update()

        # 4. Schedule the Fullscreen Lock 200ms from now
        self.after(200, self.enforce_fullscreen)

        # 5. NOW turn on the camera
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.pushup_counter = PushupCounter()

        if not self.cap.isOpened():
            print("Error: Could not open video device.")
            self.video_label.configure(text="Camera Error! Please check connection.")
            return

        # 6. Start the loop
        self.update_video_feed()

    def enforce_fullscreen(self):
        """ Applies the inescapable lock screen properties after the OS registers the window """
        self.state('zoomed')  # Natively maximizes the window in Windows
        self.attributes('-fullscreen', True)  # Strips the taskbar and borders
        self.attributes('-topmost', True)  # Forces it above all other apps
        self.protocol("WM_DELETE_WINDOW", self.disable_close_event)
        self.focus_force()  # Steals keyboard input
        self.grab_set()  # Steals mouse input

    def disable_close_event(self):
        """ Prevents closing the window via normal OS methods. """
        pass

    def update_video_feed(self) -> None:
        success, frame = self.cap.read()

        if success:
            # Flip frame horizontally for a mirror (selfie) effect
            frame = cv2.flip(frame, 1)

            # Process the frame via MediaPipe
            processed_frame, current_count = self.pushup_counter.process_frame(frame)

            # Update the UI counter
            self.counter_label.configure(text=f"{current_count} / {self.target_pushups}")

            # Check if target is reached
            if current_count >= self.target_pushups:
                self.unlock_system()
                return  # Break the loop

            # Convert BGR to RGB for PIL
            color_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image and resize it
            pil_img = Image.fromarray(color_frame)
            pil_img = pil_img.resize((800, 600), Image.Resampling.LANCZOS)

            # Convert to ImageTk for Tkinter/CustomTkinter display
            photo_image = ImageTk.PhotoImage(image=pil_img)

            # Update the label with the new image frame
            self.video_label.configure(image=photo_image, text="")
            self.video_label.image = photo_image  # Keep reference to avoid garbage collection

        else:
            print("Failed to grab frame from camera.")

        # Schedule the next frame update (approx 60 FPS)
        self.after(15, self.update_video_feed)

    def release_resources(self):
        """ Safely release the camera. """
        if self.cap.isOpened():
            self.cap.release()

    def unlock_system(self):
        """ Handles the unlock procedure. """
        self.release_resources()
        if self.on_unlock_callback:
            self.on_unlock_callback()
        self.destroy()