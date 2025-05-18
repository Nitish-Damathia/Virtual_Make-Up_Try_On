import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

LIPS_IDX = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
            375, 321, 405, 314, 17, 84, 181, 91, 146, 61]
LEFT_EYE_UPPER = [33, 160, 158, 133]
RIGHT_EYE_UPPER = [362, 385, 387, 263]

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))  # BGR

def apply_makeup(frame, product):
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    color = hex_to_bgr(product["color"])

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            if product["type"] == "lipstick":
                lips = [(int(face_landmarks.landmark[idx].x * w),
                         int(face_landmarks.landmark[idx].y * h)) for idx in LIPS_IDX]
                overlay = frame.copy()
                cv2.fillPoly(overlay, [np.array(lips, np.int32)], color)
                frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
            elif product["type"] == "eyeliner":
                for eye in [LEFT_EYE_UPPER, RIGHT_EYE_UPPER]:
                    points = [(int(face_landmarks.landmark[i].x * w),
                               int(face_landmarks.landmark[i].y * h)) for i in eye]
                    for i in range(len(points) - 1):
                        cv2.line(frame, points[i], points[i + 1], color, 2)
    return frame
