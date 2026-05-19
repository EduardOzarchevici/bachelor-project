import os
import cv2
import mediapipe as mp
import winsound  # Built-in Windows library for audio feedback
from .exercise_logic import calculate_angle  # Bring this back!

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


class PushupCounter:
    def __init__(self):
        model_path = os.path.abspath("vision/pose_landmarker_heavy.task")

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            output_segmentation_masks=False
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

        self.counter = 0
        self.stage = None
        self.anchor_wrist_y = None

    def process_frame(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        results = self.landmarker.detect(mp_image)
        image_bgr = frame.copy()

        form_warning = "Get into position!"
        debug_text = ""

        try:
            if results.pose_landmarks:
                landmarks = results.pose_landmarks[0]

                # 1. Extract both arms
                left_shoulder = landmarks[11]
                left_elbow = landmarks[13]
                left_wrist = landmarks[15]

                right_shoulder = landmarks[12]
                right_elbow = landmarks[14]
                right_wrist = landmarks[16]

                avg_wrist_y = (left_wrist.y + right_wrist.y) / 2
                shoulder_width = abs(left_shoulder.x - right_shoulder.x)

                if shoulder_width < 0.10:
                    self.stage = None
                    self.anchor_wrist_y = None
                    form_warning = "Too sideways! Turn towards camera."
                else:
                    if self.anchor_wrist_y is None:
                        self.anchor_wrist_y = avg_wrist_y

                    # DYNAMIC TRACKING: Use the Z-axis (Depth) to find the arm closest to the camera
                    if left_shoulder.z < right_shoulder.z:
                        arm_name = "Left"
                        tracking_color = (255, 150, 0)  # Blue
                        shoulder = [left_shoulder.x, left_shoulder.y]
                        elbow = [left_elbow.x, left_elbow.y]
                        wrist = [left_wrist.x, left_wrist.y]
                    else:
                        arm_name = "Right"
                        tracking_color = (0, 255, 255)  # Yellow
                        shoulder = [right_shoulder.x, right_shoulder.y]
                        elbow = [right_elbow.x, right_elbow.y]
                        wrist = [right_wrist.x, right_wrist.y]

                    # Calculate the math
                    arm_angle = calculate_angle(shoulder, elbow, wrist)
                    wrist_movement = abs(avg_wrist_y - self.anchor_wrist_y)

                    # Show exactly what the AI sees on the screen
                    debug_text = f"{arm_name} Arm Angle: {int(arm_angle)} | Movement: {wrist_movement:.2f}"

                    # Slightly relaxed tolerance for the floor anchor (10%)
                    if wrist_movement > 0.10:
                        self.stage = None
                        form_warning = "CHEATING: Hands left the floor!"
                        self.anchor_wrist_y = (self.anchor_wrist_y * 0.9) + (avg_wrist_y * 0.1)
                    else:
                        form_warning = ""

                        if arm_angle > 160:
                            self.stage = "up"

                        if arm_angle < 90 and self.stage == 'up':
                            self.stage = "down"
                            self.counter += 1
                            winsound.Beep(1200, 150)

                # --- Drawing ---
                h, w, _ = image_bgr.shape

                if 'shoulder' in locals():
                    # Thicker lines for the arm being actively tracked
                    cv2.line(image_bgr,
                             (int(shoulder[0] * w), int(shoulder[1] * h)),
                             (int(elbow[0] * w), int(elbow[1] * h)), tracking_color, 4)
                    cv2.line(image_bgr,
                             (int(elbow[0] * w), int(elbow[1] * h)),
                             (int(wrist[0] * w), int(wrist[1] * h)), tracking_color, 4)

                if form_warning:
                    cv2.putText(image_bgr, form_warning, (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                if debug_text:
                    cv2.putText(image_bgr, debug_text, (50, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        except Exception as e:
            pass

        return image_bgr, self.counter