import cv2
import numpy as np
from typing import List
import mediapipe as mp  # type: ignore
from typing import Any
from .util_func import calculate_angle


class SquatAnalyzer:
    def __init__(self, landmarks: List[Any], mp_pose: mp.solutions.pose.Pose) -> None:
        # 관절 좌표 저장
        self.hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        self.knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        self.ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        # 각도 계산 및 저장
        self.angles = {
            'knee': calculate_angle(self.hip, self.knee, self.ankle)
        }

    def is_squat(self, angle_threshold: float = 90) -> bool:
        # 무릎 각도가 threshold 이하이면 스쿼트로 판단
        return self.angles['knee'] <= angle_threshold

    def draw_pose_info(self, frame: np.ndarray) -> None:
        # 무릎 각도 표시
        h, w = frame.shape[:2]
        knee_point = tuple(np.multiply(self.knee, [w, h]).astype(int))
        cv2.putText(frame, f"Knee: {int(self.angles['knee'])}", knee_point,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (79, 121, 66), 2, cv2.LINE_AA)
        # 필요시 다른 각도, 포인트 등 추가 표시
